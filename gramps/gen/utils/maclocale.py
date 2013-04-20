#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011	John Ralls, Fremont, CA
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$
###
# Mac Localization Functions
###
"""
There is something of a mismatch between native Mac localization and
that of Gtk applications like Gramps because Apple chose to use IBM's
more modern and more complete International Components for Unicode
(ICU) for the purpose rather than the older POSIX and gettext based
localization used by Gtk (and most other Linux applications).

For Gramps, the system defaults settings will be used only if the user
hasn't set the corresponding environment variable already.

Apple's language list maps nicely to gettext's LANGUAGE environment
variable, so we use that if it's set. There's an additional
MULTI-TRANSLATION environment variable which the user can set to allow
incomplete translations to be supplemented from other translations on
the list before resorting to the default english. Many users find this
disconcerting, though, so it's not enabled by default. If the user
hasn't set a translation list (this happens occasionally), we'll check
the locale and collation settings and use either to set $LANGUAGE if
it's set to a non-english locale.

Similarly, Apple provides an "Order for sorted lists" which maps
directly to LC_COLLATE, and a Format>Region which maps to LANG. (Those
are the names of the controls in System Preferences; the names in the
defaults system are AppleCollationOrder and AppleLocale,
respectively.)

The user can override the currency and calendar, and those values are
appended to AppleLocale and parsed below. But Gramps makes no use of
currency and sets the calendar in its own preferences, so they're
ignored.

Where the mismatch becomes a problem is in date and number
formatting. POSIX specifies a locale for this, but ICU uses format
strings, and there is no good way to map those strings into one of the
available locales. Users who whan to specify particular ways of
formatting different from their base locales will have to figure out
the appropriate locale on their own and set LC_TIME and LC_NUMERIC
appropriately. The "Formats" page on the Languages & Text
(International in Leopard) System Preferences pane is a good way to
quickly assess the formats in various locales.

Neither Gramps nor Gtk supply a separate English translation, so if we
encounter English in the language list we substitute "C"; if we must
set $LANGUAGE from either locale or collation, we ignore an English
locale, leaving $LANGUAGE unset (which is the same as setting it to
"C".

"""
# $Id$

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------

import sys, os, subprocess
import logging
LOG = logging.getLogger("grampslocale")

def mac_setup_localization(glocale):
    """
    Set up the localization parameters from OSX's "defaults" system,
    permitting environment variables to override the settings.
    """
    defaults = "/usr/bin/defaults"
    find = "/usr/bin/find"
    locale_dir = "/usr/share/locale"

    def _mac_get_gramps_defaults(pref):
        try:
            answer = subprocess.Popen(
                [defaults,  "read", "-app", "Gramps", pref],
                stderr=open("/dev/null"),
                stdout=subprocess.PIPE).communicate()[0]
            if not answer:
                answer = subprocess.Popen(
                    [defaults, "read", "-g", pref],
                stderr=open("/dev/null"),
                stdout=subprocess.PIPE).communicate()[0]
                if not answer:
                    return None
            if not sys.version_info[0] < 3:
                answer = answer.decode("utf-8")
            return answer
        except OSError as err:
            LOG.warning("Failed to load localization defaults from System Preferences: %s", str(err))
            return None

    def mac_language_list():
        """
        Extract the languages list from defaults.
        """
        languages = _mac_get_gramps_defaults("AppleLanguages")
        if not languages:
            return []
        languages = map(lambda x: x.strip(),
                        languages.strip("()\n").split(",\n"))
        usable = []
        for lang in languages:
            lang = lang.strip().strip('"').replace("-", "_", 1)
            if lang == "cn_Hant": #Traditional; Gettext uses cn_TW
                lang = "cn_TW"
            if lang == "cn_Hans": #Simplified; Gettext uses cn_CN
                lang = "cn_CN"
            lang = glocale.check_available_translations(lang)
            if lang:
                usable.append(lang)

        return usable

    def mac_get_locale():
        """
        Get the locale and specifiers from defaults.
        """
        locale = ""
        calendar = ""
        currency = ""
#Note that numeric separators are encoded in AppleICUNumberSymbols,
#with [0] being the decimal separator and [1] the thousands
#separator. This obviously won't translate into a locale without
#searching the locales database for a match.
        default_locale = _mac_get_gramps_defaults("AppleLocale")
        if not default_locale:
            return (locale, calendar, currency)

        div = default_locale.strip().split(b"@")
        locale = div[0]
        if len(div) > 1:
            div = div[1].split(";")
            for phrase in div:
                (name, value) = phrase.split("=")
                if name == "calendar":
                    calendar = value
                elif name == "currency":
                    currency = value

        return (locale, calendar, currency)

    def mac_get_collation():
        """
        Extract the collation (sort order) locale from the defaults string.
        """
        apple_collation = _mac_get_gramps_defaults("AppleCollationOrder")
        apple_collation = apple_collation.strip()
        if apple_collation.startswith("root"):
            return (None, None)
        div = apple_collation.split(b"@")
        collation = div[0]
        qualifier = None
        if len(div) > 1:
            parts = div[1].split(b"=")
            if len(parts) == 2 and parts[0] == 'collation':
                qualifier = parts[1]
        return (collation, qualifier)


# The action starts here

    (loc, currency, calendar)  = mac_get_locale()
    if "LC_COLLATE" in os.environ:
        collation = os.environ["LC_COLLATE"]
    else:
        (collation, coll_qualifier) = mac_get_collation()

    if not glocale.lang:
        lang = None
        if "LANG" in os.environ:
            lang = glocale.check_available_translations(os.environ["LANG"])

        if not lang:
            lang = glocale.check_available_translations(loc)
        if not lang and collation != None:
            lang = glocale.check_available_translations(collation)

        if not lang:
            LOG.warning("No locale settings matching available translations found, using US English")
            lang = 'C'

        glocale.lang = lang

    if not glocale.language:
        language = None
        if "LANGUAGE" in os.environ:
            language =  [x for x in [glocale.check_available_translations(l)
                                     for l in os.environ["LANGUAGE"].split(":")]
                         if x]
        if (not language and "LANG" in os.environ
            and not os.environ['LANG'].startswith("en_US")):
            lang = glocale.check_available_translations(os.environ['LANG'])
            if lang:
                language = [lang]

        if not language:
            translations = mac_language_list()
            if len(translations) > 0:
                language = translations


        if not language:
            language = [glocale.lang[:5]]

        glocale.language = language

    if (currency and "LC_MONETARY" not in os.environ
        and "LANG" not in os.environment):
        glocale.currency = currency
        os.environ["LC_MONETARY"] = currency
    elif "LC_MONETARY" in os.environ:
        glocale.currency = os.environ[LC_MONETARY]
    else:
        glocale.currency = glocale.lang[:5]

    if (calendar and "LC_TIME" not in os.environ
        and "LANG" not in os.environ):
        glocale.calendar = calendar
        os.environ["LC_TIME"] = calendar
    elif "LC_TIME" in os.environ:
        glocale.calendar = os.environ["LC_TIME"]
    else:
        glocale.calendar = glocale.lang[:5]

    if (collation and "LC_COLLATION" not in os.environ
        and "LANG" not in os.environ):
        glocale.collation = collation
        glocale.coll_qualifier = qualifier
        os.environ["LC_COLLATION"] = calendar
    elif "LC_COLLATION" in os.environ:
        glocale.collation = os.environ["LC_COLLATION"]
    else:
        glocale.collation = glocale.lang[:5]

    if "LC_NUMERIC" in os.environ:
        glocale.numeric = os.environ["LC_NUMERIC"]
    else:
        glocale.numeric = glocale.lang[:5]


