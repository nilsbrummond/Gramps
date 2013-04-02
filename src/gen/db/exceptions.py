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

# $Id$

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
    
class DbTransactionCancel(Exception):
    """
    Error used to indicate that a transaction needs to be canceled,
    for example becuase it is lengthy and the users requests so.
    """
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        return self.value

class DbVersionError(Exception):
    """
    Error used to report that a file could not be read because it is written 
    in an unsupported version of the file format.
    """
    def __init__(self, tree_vers, min_vers, max_vers):
        Exception.__init__(self)
        self.tree_vers = tree_vers
        self.min_vers = min_vers
        self.max_vers = max_vers

    def __str__(self):
        return _("The schema version is not supported by this version of "
                 "Gramps.\n\n"
                 "This Family tree is schema version %(tree_vers)s, and this "
                 "version of Gramps supports versions %(min_vers)s to "
                 "%(max_vers)s\n\n"
                 "Please upgrade to the corresponding version or use "
                 "XML for porting data between different database versions.") %\
                 {'tree_vers': self.tree_vers,
                  'min_vers': self.min_vers,
                  'max_vers': self.max_vers}
    
class BsddbDowngradeError(Exception):
    """
    Error used to report that the Berkeley database used to create the family
    tree is of a version that is too new to be supported by the current version.
    """
    def __init__(self, env_version, bdb_version):
        Exception.__init__(self)
        self.env_version = str(env_version)
        self.bdb_version = str(bdb_version)

    def __str__(self):
        return _('Gramps stores its data in a Berkeley Database. '
                 'The family tree you try to load was created with version '
                 '%(env_version)s of the Berkeley DB. However, the Gramps '
                 'version in use right now employs version %(bdb_version)s '
                 'of the Berkeley DB. So you are trying to load data created '
                 'in a newer format into an older program; this is bound to '
                 'fail. The right approach in this case is to use XML export '
                 'and import. So try to open the family tree on that computer '
                 'with that software that created the family tree, export it '
                 'to XML and load that XML into the version of Gramps you '
                 'intend to use.') % {'env_version': self.env_version,
                 'bdb_version': self.bdb_version}

class BsddbUpgradeRequiredError(Exception):
    """
    Error used to report that the Berkeley database used to create the family
    tree is of a version that is too new to be supported by the current version.
    """
    def __init__(self, env_version, bsddb_version):
        Exception.__init__(self)
        self.env_version = str(env_version)
        self.bsddb_version = str(bsddb_version)

    def __str__(self):
        return _('The BSDDB version of the Family Tree you are trying to open '
              'needs to be upgraded from %(env_version)s to %(bdb_version)s.\n\n'
              'This probably means that the Family Tree was created with '
              'an old version of Gramps. Opening the tree with this version '
              'of Gramps may irretrievably corrupt your tree. You are '
              'strongly advised to backup your tree before proceeding, '
              'see: \n'
              'http://www.gramps-project.org/wiki/index.php?title=How_to_make_a_backup\n\n'
              'If you have made a backup, then you can get Gramps to try '
              'to open the tree and upgrade it') % \
              {'env_version': self.env_version,
               'bdb_version': self.bsddb_version}

class DbEnvironmentError(Exception):
    """
    Error used to report that the database 'environment' could not be opened.
    Most likely, the database was created by a different version of the underlying database engine.
    """
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return (_("Gramps has detected a problem in opening the 'environment' "
                  "of the underlying Berkeley database used to store this Family Tree. "
                  "The most likely cause "
                  "is that the database was created with an old version "
                  "of the Berkeley database program, and you are now using a new version. "
                  "It is quite likely that your database has not been "
                  "changed by Gramps.\nIf possible, you should revert to your "
                  "old version of Gramps and its support software; export "
                  "your database to XML; close the database; then upgrade again "
                  "to this version of Gramps and import the XML file "
                  "in an empty Family Tree. Alternatively, it may be possible "
                  "to use the Berkeley database recovery tools.")
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
