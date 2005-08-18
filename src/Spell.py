#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005  Donald N. Allingham
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

"""
Provide an interface to the gtkspell interface. This requires
python-gnome-extras package. If the gtkspell package is not
present, we default to no spell checking.

"""

#### FIXME: Uncomment after 2.0.6 is released.

## success = False
## try:
##     import gtk
##     import gtkspell
##     import locale

##     text_view = gtk.TextView()
##     spell = gtkspell.Spell(text_view)
##     lang = locale.getlocale()[0]
##     spell.set_language(lang)
##     success = True

## except ImportError, msg:
##     print "Spell.py:", msg
## except RuntimeError,msg:
##     print "Spell.py:", msg
## except SystemError,msg:
##     print "Spell.py:", msg

if False:
    class Spell:
        def __init__(self,obj):
            self.spell = gtkspell.Spell(obj)
            lang = locale.getlocale()[0]
            self.spell.set_language(lang)
else:
    class Spell:
        def __init__(self,obj):
            pass
