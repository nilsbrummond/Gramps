#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Marker types.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib.grampstype import GrampsType

class MarkerType(GrampsType):
    """
    Class for handling data markers.
    """

    NONE      = -1
    CUSTOM    = 0
    COMPLETE  = 1
    TODO_TYPE = 2

    _CUSTOM = CUSTOM
    _DEFAULT = NONE

    _DATAMAP = [
        (NONE,      "",   ""),
        (CUSTOM,    _("Custom"),   "Custom"),
        (COMPLETE,  _("Complete"), "Complete"),
        (TODO_TYPE, _("ToDo"),     "ToDo"),
        ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def set(self, value):
        """
        Set the marker value.
        """
        if isinstance(value, self.__class__):
            if value.val == self.CUSTOM and value.string == u'':
                self.val = self.NONE
                self.string = u''
            else:
                self.val = value.val
                self.string = value.string
        elif isinstance(value, tuple):
            if value[0] == self.CUSTOM and value[1] == u'':
                self.value = self.NONE
                self.string = u''
            else:
                self.val = value[0]
                self.string = value[1]
        elif isinstance(value, int):
            self.val = value
            self.string = u''
        elif isinstance(value, str):
            self.val = self._S2IMAP.get(value, self._CUSTOM)
            if self.val == self._CUSTOM:
                self.string = value
            else:
                self.string = u''
        else:
            self.val = self._DEFAULT
            self.string = u''
