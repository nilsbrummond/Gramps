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

# test/LosHawlos_dbtest.py
# $Id$

import os
import tempfile
import shutil
import sys

sys.path.append('../gramps')

import GrampsDb
import const
import RelLib

def dummy_callback(dummy):
    pass

def add_source( db,title,commit=True,fail=False):
    tran = db.transaction_begin()
    db.disable_signals()
    s = RelLib.Source()
    db.add_source(s,tran)
    s.set_title(title)
    if fail:
        return # Fail here
    db.commit_source(s,tran)
    db.enable_signals()
    if commit:
        db.transaction_commit(tran, "Add Source")

def add_person( db,firstname,lastname,commit=True,fail=False):
    tran = db.transaction_begin()
    db.disable_signals()
    p = RelLib.Person()
    db.add_person(p,tran)
    n = RelLib.Name()
    n.set_first_name(firstname)
    n.set_surname(lastname)
    p.set_primary_name(n)
    if fail:
        return # Fail here
    db.commit_person(p,tran)
    db.enable_signals()
    if commit:
        db.transaction_commit(tran, "Add Person")

def print_db_content(db):
    for h in db.get_person_handles():
        print "DB contains: person %s" % h
    for h in db.get_source_handles():
        print "DB contains: source %s" % h

tmpdir = tempfile.mkdtemp()
try:
    filename1 = os.path.join(tmpdir,'test1.grdb')
    filename2 = os.path.join(tmpdir,'test2.grdb')
    print "\nUsing Database file: %s" % filename1
    db = GrampsDb.gramps_db_factory(const.app_gramps)()
    db.load( filename1, dummy_callback, "w")
    print "Add person 1"
    add_person( db,"Anton", "Albers",True,False)
    print "Add source"
    add_source( db,"A short test",True,False)
    print "Add person 2 without commit"
    add_person( db,"Bernd","Beta",False,False)
    print "Add source"
    add_source( db,"A short test",True,False)
    print "Add person 3"
    add_person( db,"Chris","Connor",True,False)
    print_db_content( db)    
    print "Closing Database file: %s" % filename1
    #db.close()

    print "\nUsing Database file: %s" % filename1
    db = GrampsDb.gramps_db_factory(const.app_gramps)()
    db.load( filename1, dummy_callback, "w")
    print "Add person 4"
    add_person( db,"Felix", "Fowler",True,False)
    print "Add person 4"
    add_person( db,"Felix", "Fowler",False,False)
    print_db_content( db)    
    print "Closing Database file: %s" % filename1
    #db.close()

    print "\nUsing Database file: %s" % filename2
    db = GrampsDb.gramps_db_factory(const.app_gramps)()
    db.load( filename2, dummy_callback, "w")

    print "Add source"
    add_source( db,"A short test",False,False)
    print "Add source 2 will fail"
    add_source( db,"Bang bang bang",True,True)

    print_db_content( db)    
    print "Closing Database file: %s" % filename2
    #db.close()
finally:
    print "Exit. Cleaning up."
    shutil.rmtree(tmpdir)
