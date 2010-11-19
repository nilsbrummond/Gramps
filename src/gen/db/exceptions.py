#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005 Donald N. Allingham
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

# $Id:exceptions.py 9912 2008-01-22 09:17:46Z acraphae $

"""Exceptions generated by the Db package."""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _


class DbException(Exception):
    
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value
        
    def __str__(self):
        return self.value

class DbWriteFailure(Exception):
    """
    Error used to indicate that a write to a database has failed.
    """
    def __init__(self, value, value2=""):
        Exception.__init__(self)
        self.value = value
        self.value2 = value2
        
    def __str__(self):
        return self.value
    
    def messages(self):
        return self.value, self.value2
    
class DbVersionError(Exception):
    """
    Error used to report that a file could not be read because it is written 
    in an unsupported version of the file format.
    """
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return _("The database version is not supported by this version of "
                 "Gramps.\nPlease upgrade to the corresponding version or use "
                 "XML for porting data between different database versions.")
    
class DbEnvironmentError(Exception):
    """
    Error used to report that the database 'environment' could not be opened.
    Most likely, the database was created by a different version of the underlying database engine.
    """
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return (_("Gramps has detected an problem in opening the 'environment' "
                  "of the underlying Berkeley database. The most likely cause "
                  "is that the database was created with an old version "
                  "of the Berkeley database, and you are now using a new version. "
                  "It is quite likely that your database has not been "
                  "changed by Gramps.\nIf possible, you could revert to your "
                  "old version of Gramps and its support software; export "
                  "your database to XML; close the database; then upgrade again "
                  "to this version "
                  "and import the XML file. Alternatively, it may be possible "
                  "to upgrade your database.")
                  + '\n\n' + str(self.msg))
    
class DbUpgradeRequiredError(Exception):
    """
    Error used to report that a database needs to be upgraded before it can be 
    used.
    """
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return _("You cannot open this database without upgrading it.\n"
                 "If you upgrade then you won't be able to use previous "
                 "versions of Gramps.\n"
                 "You might want to make a backup copy first.")
