#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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
This package implements an object difference engine.
"""

import os

from gramps.cli.user import User
from ..dbstate import DbState
from gramps.cli.grampscli import CLIManager
from ..plug import BasePluginManager
from ..db.dictionary import DictionaryDb
from gramps.gen.lib.handle import Handle
from ..const import GRAMPS_LOCALE as glocale
from ..constfunc import handle2internal
_ = glocale.translation.gettext

def import_as_dict(filename, user=None):
    """
    Import the filename into a DictionaryDb and return it.
    """
    if user is None:
        user = User()
    db = DictionaryDb()
    dbstate = DbState()
    climanager = CLIManager(dbstate, setloader=False, user=user)
    climanager.do_reg_plugins(dbstate, None)
    pmgr = BasePluginManager.get_instance()
    (name, ext) = os.path.splitext(os.path.basename(filename))
    format = ext[1:].lower()
    import_list = pmgr.get_reg_importers()
    for pdata in import_list:
        if format == pdata.extension:
            mod = pmgr.load_plugin(pdata)
            if not mod:
                for item in pmgr.get_fail_list():
                    name, error_tuple, pdata = item
                    # (filename, (exception-type, exception, traceback), pdata)
                    etype, exception, traceback = error_tuple
                    #print("ERROR:", name, exception)
                return False
            import_function = getattr(mod, pdata.import_function)
            import_function(db, filename, user)
            return db
    return None

def diff_dates(json1, json2):
    """
    Compare two json date objects. Returns True if different.
    """
    if json1 == json2: # if same, then Not Different
        return False   # else, they still might be Not Different
    elif isinstance(json1, dict) and isinstance(json2, dict):
        if json1["dateval"] == json2["dateval"] and json2["dateval"] != 0:
            return False
        elif json1["text"] == json2["text"]:
            return False
        else:
            return True
    else:
        return True

def diff_items(path, json1, json2):
    """
    Compare two json objects. Returns True if different.
    """
    if json1 == json2:
        return False
    elif isinstance(json1, Handle) and isinstance(json2, Handle):
        return not (json1.classname == json2.classname and
                    json1.handle == json2.handle)
    elif isinstance(json1, list) and isinstance(json2, list):
        if len(json1) != len(json2):
            return True
        else:
            pos = 0
            for v1, v2 in zip(json1, json2):
                result = diff_items(path + ("[%d]" % pos), v1, v2)
                if result:
                    return True
                pos += 1
            return False
    elif isinstance(json1, dict) and isinstance(json2, dict):
        for key in json1.keys():
            if key == "change":
                continue # don't care about time differences, only data changes
            elif key == "date":
                result = diff_dates(json1["date"], json2["date"])
                if result:
                    #print("different dates", path)
                    #print("   old:", json1["date"])
                    #print("   new:", json2["date"])
                    return True
            else:
                result = diff_items(path + "." + key, json1[key], json2[key])
                if result:
                    return True
        return False
    else:
        #print("different values", path)
        #print("   old:", json1)
        #print("   new:", json2)
        return True

def diff_dbs(db1, db2, user=None):
    """
    1. new objects => mark for insert 
    2. deleted objects, no change locally after delete date => mark
       for deletion
    3. deleted objects, change locally => mark for user confirm for 
       deletion
    4. updated objects => do a diff on differences, mark origin
       values as new data
    """
    if user is None:
        user = User()
    missing_from_old = []
    missing_from_new = []
    diffs = []
    with user.progress(_('Family Tree Differences'), 
            _('Searching...'), 10) as step:
        for item in ['Person', 'Family', 'Source', 'Citation', 'Event', 'Media',
                     'Place', 'Repository', 'Note', 'Tag']:
            step()
            handles1 = sorted([handle2internal(handle) for handle in db1._tables[item]["handles_func"]()])
            handles2 = sorted([handle2internal(handle) for handle in db2._tables[item]["handles_func"]()])
            p1 = 0
            p2 = 0
            while p1 < len(handles1) and p2 < len(handles2):
                if handles1[p1] == handles2[p2]: # in both
                    item1 = db1._tables[item]["handle_func"](handles1[p1])
                    item2 = db2._tables[item]["handle_func"](handles2[p2])
                    diff = diff_items(item, item1.to_struct(), item2.to_struct())
                    if diff:
                        diffs += [(item, item1, item2)]
                    # else same!
                    p1 += 1
                    p2 += 1
                elif handles1[p1] < handles2[p2]: # p1 is mssing in p2
                    item1 = db1._tables[item]["handle_func"](handles1[p1])
                    missing_from_new += [(item, item1)]
                    p1 += 1
                elif handles1[p1] > handles2[p2]: # p2 is mssing in p1
                    item2 = db2._tables[item]["handle_func"](handles2[p2])
                    missing_from_old += [(item, item2)]
                    p2 += 1
            while p1 < len(handles1):
                item1 = db1._tables[item]["handle_func"](handles1[p1])
                missing_from_new += [(item, item1)]
                p1 += 1
            while p2 < len(handles2):
                item2 = db2._tables[item]["handle_func"](handles2[p2])
                missing_from_old += [(item, item2)]
                p2 += 1
    return diffs, missing_from_old, missing_from_new 

def diff_db_to_file(old_db, filename, user=None):
    if user is None:
        user = User()
    # First, get data as a DictionaryDb
    new_db = import_as_dict(filename, user, user)
    # Next get differences:
    diffs, m_old, m_new = diff_dbs(old_db, new_db, user)
    return diffs, m_old, m_new
    
