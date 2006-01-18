#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
Provides the GRAMPS DB interface for supporting in-memory editing
of GEDCOM files.
"""

from RelLib import *
from _GrampsInMemDB import *

import _ReadGedcom as ReadGedcom
import _WriteGedcom as WriteGedcom

#-------------------------------------------------------------------------
#
# GrampsGEDDB
#
#-------------------------------------------------------------------------
class GrampsGEDDB(GrampsInMemDB):
    """GRAMPS database object. This object is a base class for other
    objects."""

    def __init__(self):
        """creates a new GrampsDB"""
        GrampsInMemDB.__init__(self)

    def load(self,name,callback, mode="w"):
        if self.db_is_open:
            self.close()
        GrampsInMemDB.load(self,name,callback,mode)
        ReadGedcom.importData(self,name,callback,use_trans=False)

        self.bookmarks = self.metadata.get('bookmarks')
        if self.bookmarks == None:
            self.bookmarks = []
        self.db_is_open = True
        return 1

    def close(self):
        if not self.db_is_open:
            return
        if not self.readonly and len(self.undodb) > 0:
            writer = WriteGedcom.GedcomWriter(self,self.get_default_person())
            writer.export_data(self.filename)
        self.db_is_open = False

