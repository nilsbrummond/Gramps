#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Brian G. Matherly
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import gettext
import sys
import os
import locale
import logging
LOG = logging.getLogger("grampslocale")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter(fmt="%(name)s.%(levelname)s: %(message)s"))
LOG.addHandler(_hdlr)
HAVE_ICU = False
try:
    from icu import Locale, Collator
    HAVE_ICU = True
except ImportError:
    try:
        from PyICU import Locale, Collator
        HAVE_ICU = True
    except ImportError as err:
        LOG.warning("ICU is not installed because %s, localization will be impaired", str(err))
#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ..const import LOCALE_DIR
from ..constfunc import mac, win, UNITYPE

#------------------------------------------------------------------------
#
# GrampsLocale Class
#
#------------------------------------------------------------------------
class GrampsLocale(object):
    """
    Encapsulate a locale.  This class is a sort-of-singleton: The
    first instance created will query the environment and OSX defaults
    for missing parameters (precedence is parameters passed to the
    constructor, environment variables LANG, LC_COLLATE, LC_TIME,
    etc., and LANGUAGE, OSX defaults settings when that's the
    platform).  Subsequent calls to the constructor with no or
    identical parameters will return the same Grampslocale
    object. Construction with different parameters will result in a
    new GrampsLocale instance with the specified parameters, but any
    parameters left out will be filled in from the first instance.

    @localedir: The full path to the top level directory containing
                the translation files. Defaults to sys.prefix/share/locale.

    @lang:      A single locale value which is used for unset locale.LC_FOO
                settings.

    @domain:    The name of the applicable translation file. The default is
                "gramps", indicating files in LC_MESSAGES named gramps.mo.

    @languages: A list of two or five character codes corresponding to
                subidrectries in the localedir, e.g. "fr" or "zh_CN".
    """
    __first_instance = None
    def __new__(cls, localedir=None, lang=None, domain=None, languages=None):
        if not GrampsLocale.__first_instance:
            cls.__first_instance = super(GrampsLocale, cls).__new__(cls)
            cls.__first_instance.initialized = False
            return cls.__first_instance

        if not cls.__first_instance.initialized:
            raise RuntimeError("Second GrampsLocale created before first one was initialized")
        if ((lang is None or lang == cls.__first_instance.lang)
            and (localedir is None or localedir == cls.__first_instance.localedir)
            and (domain is None or domain == cls.__first_instance.localedomain)
            and (languages is None or len(languages) == 0 or
                 languages == cls.__first_instance.languages)):
            return cls.__first_instance

        return super(GrampsLocale, cls).__new__(cls)

    def __init_from_environment(self, lang=None, language=None):
        if not lang:
            lang = ' '
            try:
                lang = os.environ["LANG"]
            except KeyError:
                lang = locale.getlocale()[0]
                if not lang:
                    try:
                        lang = locale.getdefaultlocale()[0] + '.UTF-8'
                    except TypeError:
                        LOG.warning('Unable to determine your Locale, using English')
                        lang = 'C.UTF-8'
            self.lang = lang

        if not language or len(language) == 0:
            if "LANGUAGE" in os.environ:
                avail =  self.get_available_translations()
                language = [l for l in os.environ["LANGUAGE"].split(":")
                            if l[:5] in avail or l[:2] in avail]
                self.language = language
            elif not lang == "C.UTF-8":
                self.language = [lang]
            else:
                self.language = ["en"]

            if "LC_MONETARY" not in os.environ:
                self.currency = lang
            else:
                self.currency = os.environ["LC_MONETARY"]

            if "LC_TIME" not in os.environ:
                self.calendar = lang
            else:
                self.calendar = os.environ["LC_TIME"]

            if "LC_COLLATE" not in os.environ:
                self.collation = lang
            else:
                self.collation = os.environ["LC_COLLATE"]

    def _win_bindtextdomain(self, localedomain, localedir):
        """
        Help routine for loading and setting up libintl attributes
        Returns libintl
        """
        from ctypes import cdll
        try:
            libintl = cdll.LoadLibrary('libintl-8')
            libintl.bindtextdomain(localedomain,
                                   localedir.encode(sys.getfilesystemencoding()))
            libintl.textdomain(localedomain)
            libintl.bind_textdomain_codeset(localedomain, "UTF-8")
            print("Set domain %s in %s" % (localedomain, localedir))
        except WindowsError:
            LOG.warning("Localization library libintl not on %PATH%, localization will be incomplete")


    def __init_first_instance(self, localedir=None, lang=None,
                              domain=None, language=None):

#First, globally set the locale to what's in the environment:
        locale.setlocale(locale.LC_ALL, '')

        if localedir and os.path.exists(localedir):
            self.localedir = localedir
        else:
            if ("GRAMPSI18N" in os.environ
                and os.path.exists(os.environ["GRAMPSI18N"])):
                self.localedir = os.environ["GRAMPSI18N"]
            elif os.path.exists(LOCALE_DIR):
                self.localedir = LOCALE_DIR
            elif os.path.exists(os.path.join(sys.prefix, "share", "locale")):
                self.localedir = os.path.join(sys.prefix, "share", "locale")
            else:
                if not lang:
                    lang = os.environ.get('LANG', 'en')
                if lang and lang[:2] == 'en':
                    pass # No need to display warning, we're in English
                else:
                    LOG.warning('Locale dir does not exist at %s', LOCALE_DIR)
                    LOG.warning('Running python setup.py install --prefix=YourPrefixDir might fix the problem')

        if not self.localedir:
#No localization files, no point in continuing
            return
        if domain:
            self.localedomain = domain
        else:
            self.localedomain = 'gramps'

        if not language or not isinstance(language, list):
            language = []
        else:
            language = [l for l in languages
                        if l in get_available_translations()]

        if mac():
            from . import maclocale
            maclocale.mac_setup_localization(self, lang, language)
        else:
            self.__init_from_environment(lang, language)
#A variety of useful functions use the current locale for
#formatting. Pending global replacement of those functions with ICU
#equivalents, we need to use setlocale to our chosen default. This
#unfortunately doesn't work in Windows because it uses different
#values until VS2012 (which only works on Win8), so while we can set
#translations and date formats with lang, we can't affect currency or
#numeric format. Those are fixed by the user's system settings.

        if not win():
            locale.setlocale(locale.LC_COLLATE, self.collation)
            locale.setlocale(locale.LC_TIME, self.calendar)
            locale.setlocale(locale.LC_MONETARY, self.currency)
#Next, we need to know what is the encoding from the native environment:
        self.encoding = locale.getlocale()[1]
#GtkBuilder depends on reading Glade files as UTF-8 and crashes if it
#doesn't, so set $LANG to have a UTF-8 locale. NB: This does *not*
#affect locale.getpreferredencoding() or sys.getfilesystemencoding()
#which are set by python long before we get here.
        check_lang = self.lang.split('.')
        if len(check_lang) < 2  or check_lang[1] not in ["utf-8", "UTF-8"]:
            self.lang = '.'.join((check_lang[0], 'UTF-8'))
            os.environ["LANG"] = self.lang
        os.environ["LANGUAGE"] = ':'.join(self.language)

        # GtkBuilder uses GLib's g_dgettext wrapper, which oddly is bound
        # with locale instead of gettext. Win32 doesn't support bindtextdomain.
        if not win():
            locale.bindtextdomain(self.localedomain, self.localedir)
        else:
            self._win_bindtextdomain(self.localedomain, self.localedir)

        self.initialized = True


    def __init__(self, lang=None, localedir=None, domain=None, languages=None):
        """
        Init a GrampsLocale. Run __init_first_instance() to set up the
        environement if this is the first run. Return __first_instance
        otherwise if called without arguments.
        """
        if self == self._GrampsLocale__first_instance:
            if not self.initialized:
                self._GrampsLocale__init_first_instance(lang, localedir,
                                                        domain, languages)
            else:
                return

        else:
            if domain:
                self.localedomain = domain
            else:
                self.localedomain = self._GrampsLocale__first_instance.localedomain
            if localedir:
                self.localedir = localedir
            else:
                self.localedir = self._GrampsLocale__first_instance.localedir

            self.language = []
            if languages and len(languages) > 0:
                self.language = [l for l in languages
                                 if l in get_available_translations()]
            if len(self.language) == 0:
                self.language = self._GrampsLocale__first_instance.language

            if lang:
                self.lang = lang
            else:
                self.lang = self._GrampsLocale__first_instance.lang

            self.collation = self.currency = self.calendar = self.lang

        self.icu_locales = {}
        self.collator = None
        if HAVE_ICU:
            self.icu_locales["default"] = Locale.createFromName(self.lang)
            if self.collation != self.lang:
                self.icu_locales["collation"] = Locale.createFromName(self.collation)
            else:
                self.icu_locales["collation"] = self.icu_locales["default"]
            try:
                self.collator = Collator.createInstance(self.icu_locales["collation"])
            except ICUError as err:
                LOG.warning("Unable to create collator: %s", str(err))
                self.collator = None

        self.translation = self._get_translation(self.localedomain,
                                                 self.localedir, self.language)
        self._set_dictionaries()




    def _get_translation(self, domain = None,
                         localedir = None,
                         languages=None):
        """
        Get a translation of one of our classes. Doesn't return the
        singleton so that it can be used by get_addon_translation()
        """
        if not domain:
            domain = self.localedomain
        if not languages:
            languages = self.language
        if not localedir:
            localedir = self.localedir

        lang = gettext.find(domain, localedir, languages)
        if lang:
            translator = gettext.translation(domain, localedir,
                                             languages,
                                             class_ = GrampsTranslations)
            translator._language = os.path.basename(os.path.dirname(os.path.dirname(lang))).split('.')[0]
            return translator

        else:
            if not languages == ["en"]:
                LOG.debug("Unable to find translations for %s and %s in %s",
                          domain, languages, localedir)
            return GrampsNullTranslations()

    def _set_dictionaries(self):
        """
        Create a dictionary of language names localized to the
        GrampsLocale's primary language, keyed by language and
        country code.
        """
        _ = self.translation.gettext
        self.lang_map = {
            "bg" : _("Bulgarian"),
            "ca" : _("Catalan"),
            "cs" : _("Czech"),
            "da" : _("Danish"),
            "de" : _("German"),
            "el" : _("Greek"),
            "en" : _("English"),
            "eo" : _("Esperanto"),
            "es" : _("Spanish"),
            "fi" : _("Finnish"),
            "fr" : _("French"),
            "he" : _("Hebrew"),
            "hr" : _("Croatian"),
            "hu" : _("Hungarian"),
            "it" : _("Italian"),
            "ja" : _("Japanese"),
            "lt" : _("Lithuanian"),
            "mk" : _("Macedonian"),
            "nb" : _("Norwegian Bokmal"),
            "nl" : _("Dutch"),
            "nn" : _("Norwegian Nynorsk"),
            "pl" : _("Polish"),
            "pt" : _("Portuguese"),
            "ro" : _("Romanian"),
            "ru" : _("Russian"),
            "sk" : _("Slovak"),
            "sl" : _("Slovenian"),
            "sq" : _("Albanian"),
            "sv" : _("Swedish"),
            "tr" : _("Turkish"),
            "uk" : _("Ukrainian"),
            "vi" : _("Vietnamese"),
            "zh" : _("Chinese")
            }

        self.country_map = {
            "BR" : _("Brazil"),
            "CN" : _("China"),
            "PT" : _("Portugal")
            }

    def _get_language_string(self, lang_code):
        """
        Given a language code of the form "lang_region", return a text string
        representing that language.
        """
        code_parts = lang_code.rsplit("_")

        lang = code_parts[0]
        if lang in self.lang_map:
            lang = self.lang_map[lang]

        country = None
        if len(code_parts) > 1:
            country = code_parts[1]
        if country in self.country_map:
            country = self.country_map[country]
            lang = "%(language)s (%(country)s)" % \
                { 'language' : lang, 'country'  : country  }

        return lang

#-------------------------------------------------------------------------
#
# Public Functions
#
#-------------------------------------------------------------------------

    def get_localedomain(self):
        """
        Get the LOCALEDOMAIN used for the Gramps application.
        Required by gui/glade.py to pass to Gtk.Builder
        """
        return self.localedomain

    def get_language_list(self):
        """
        Return the list of configured languages.  Used by
        ViewManager.check_for_updates to select the language for the
        addons descriptions.
        """
        return self.language

    def get_translation(self, domain = None, languages = None):
        """
        Get a translation object for a particular language.
        See the gettext documentation for the available functions
        >>> glocale = GrampsLocale()
        >>> _ = glocale.get_translation('foo', 'French')
        >>> _ = tr.gettext
        """

        if ((domain and not domain == self.localedomain)
            or (languages and not languages == self.language)):
            if not domain:
                domain = self.localedomain
            if not languages:
                languages = self.language
            fallback = False
            if "en" in languages:
                fallback = True
            try:
                # Don't use _get_translation because we want to fall
                # back on the singleton rather than a NullTranslation
                return gettext.translation(domain, self.localedir,
                                           languages,
                                           class_ = GrampsTranslations,
                                           fallback = fallback)
            except IOError:
                LOG.warning("None of the requested languages (%s) were available, using %s instead", ', '.join(languages), self.lang)
                return self.translation
        else:
            return self.translation

    def get_addon_translator(self, filename, domain="addon",
                             languages=None):
        """
        Get a translator for an addon.

        filename - filename of a file in directory with full path, or
                   None to get from self.
        domain   - the name of the .mo file under the LANG/LC_MESSAGES dir
        languages - a list of languages to force
        returns  - a gettext.translation object

        Example:
        _ = glocale.get_addon_translator(languages=["fr_BE.utf8"]).gettext

        See the python gettext documentation.
        Assumes path/filename
            path/locale/LANG/LC_MESSAGES/addon.mo.
        """
        gramps_translator = self._get_translation()

        path = self.localedir
        if filename:
            path = os.path.join(os.path.dirname(os.path.abspath(filename)), "locale")
        if languages:
            addon_translator = self._get_translation(domain,
                                                     path,
                                                     languages=languages)
        else:
            addon_translator = self._get_translation(domain, path)
        gramps_translator.add_fallback(addon_translator)
        return gramps_translator # with a language fallback

    def get_available_translations(self):
        """
        Get a list of available translations.

        :returns: A list of translation languages.
        :rtype: unicode[]

        """
        languages = ["en"]

        if self.localedir is None:
            return languages

        for langdir in os.listdir(self.localedir):
            mofilename = os.path.join(self.localedir, langdir,
                                      "LC_MESSAGES",
                                      "%s.mo" % self.localedomain )
            if os.path.exists(mofilename):
                languages.append(langdir)

        languages.sort()

        return languages

    def get_language_dict(self):
        '''
        return a dictionary of language names : codes for use by language
        pickers.
        '''
        langs = {}
        for code in self.get_available_translations():
            langs[self._get_language_string(code)] = code

        return langs


    def trans_objclass(self, objclass_str):
        """
        Translates objclass_str into "... %s", where objclass_str
        is 'Person', 'person', 'Family', 'family', etc.
        """
        _ = self.translation.gettext
        objclass = objclass_str.lower()
        if objclass == "person":
            return _("the person")
        elif objclass == "family":
            return _("the family")
        elif objclass == "place":
            return _("the place")
        elif objclass == "event":
            return _("the event")
        elif objclass == "repository":
            return _("the repository")
        elif objclass == "note":
            return _("the note")
        elif objclass in ["media", "mediaobject"]:
            return _("the media")
        elif objclass == "source":
            return _("the source")
        elif objclass == "filter":
            return _("the filter")
        else:
            return _("See details")

    def getfilesystemencoding(self):
        """
        If the locale isn't configured correctly, this will return
        'ascii' or 'ANSI_X3.4-1968' or some other unfortunate
        result. Current unix systems all encode filenames in utf-8,
        and Microsoft Windows uses utf-16 (which they call mbcs). Make
        sure we return the right value.
        """
        encoding = sys.getfilesystemencoding()

        if encoding in ("utf-8", "UTF-8", "utf8", "UTF8", "mbcs", "MBCS"):
            return encoding

        return "utf-8"

    def sort_key(self, string):
        """
        Return a value suitable to pass to the "key" parameter of sorted()
        """

        if HAVE_ICU and self.collator:
            #ICU can digest strings and unicode
            return self.collator.getCollationKey(string).getByteArray()
        else:
            try:
                base_locale = locale.getlocale(locale.LC_COLLATE)
                locale.setlocale(locale.LC_COLLATE, self.collation)
            #locale in Python2 can't.
                if sys.version_info[0] < 3 and isinstance(string, unicode):
                    key = locale.strxfrm(string.encode("utf-8", "replace"))
                else:
                    key = locale.strxfrm(string)

                locale.setlocale(locale.LC_COLLATE, base_locale)
            except Exception as err:
                LOG.warn("Failed to obtain key for %s because %s",
                         self.collation, str(err))
                return string

            return key

    def strcoll(self, string1, string2):
        """
        Given two localized strings, compare them and return -1 if
        string1 would sort first, 1 if string2 would, and 0 if
        they are the same.
        """
        key1 = self.sort_key(string1)
        key2 = self.sort_key(string2)
        return (-1 if key1 < key2 else (1 if key1 > key2 else 0))

#-------------------------------------------------------------------------
#
# Translations Classes
#
#-------------------------------------------------------------------------
class GrampsTranslations(gettext.GNUTranslations):
    """
    Overrides and extends gettext.GNUTranslations. See the Python gettext
    "Class API" documentation for how to use this.
    """
    def language(self):
        """
        Return the target languge of this translations object.
        """
        return self._language

    def gettext(self, msgid):
        """
        Obtain translation of gettext, return a unicode object
        :param msgid: The string to translated.
        :type msgid: unicode
        :returns: Translation or the original.
        :rtype: unicode
        """
        # If msgid =="" then gettext will return po file header
        # and that's not what we want.
        if len(msgid.strip()) == 0:
            return msgid
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ugettext(self, msgid)
        else:
            return gettext.GNUTranslations.gettext(self, msgid)

    def ngettext(self, singular, plural, num):
        """
        The translation of singular/plural is returned unless the translation is
        not available and the singular contains the separator. In that case,
        the returned value is the singular.

        :param singular: The singular form of the string to be translated.
                         may contain a context seperator
        :type singular: unicode
        :param plural: The plural form of the string to be translated.
        :type plural: unicode
        :param num: the amount for which to decide the translation
        :type num: int
        :returns: Translation or the original.
        :rtype: unicode
        """
        if sys.version_info[0] < 3:
            return gettext.GNUTranslations.ungettext(self, singular,
                                                     plural, num)
        else:
            return gettext.GNUTranslations.ngettext(self, singular,
                                                    plural, num)

    def sgettext(self, msgid, sep='|'):
        """
        Strip the context used for resolving translation ambiguities.

        The translation of msgid is returned unless the translation is
        not available and the msgid contains the separator. In that case,
        the returned value is the portion of msgid following the last
        separator. Default separator is '|'.

        :param msgid: The string to translated.
        :type msgid: unicode
        :param sep: The separator marking the context.
        :type sep: unicode
        :returns: Translation or the original with context stripped.
        :rtype: unicode
        """
        msgval = self.gettext(msgid)
        if msgval == msgid:
            sep_idx = msgid.rfind(sep)
            msgval = msgid[sep_idx+1:]
        return msgval

class GrampsNullTranslations(gettext.NullTranslations):
    """
    Extends gettext.NullTranslations to provide the sgettext method.

    Note that it's necessary for msgid to be unicode. If it's not,
    neither will be the returned string.
    """
    def sgettext(self, msgid, sep='|'):
        msgval = self.gettext(msgid)
        if msgval == msgid:
            sep_idx = msgid.rfind(sep)
            msgval = msgid[sep_idx+1:]
        return msgval

    def language(self):
        """
        The null translation returns the raw msgids, which are in English
        """
        return "en"
