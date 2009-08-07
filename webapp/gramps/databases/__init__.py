from settings import GRAMPS_PATH, GRAMPS_DATABASE

import sys
sys.path.append(GRAMPS_PATH)

from cli.argparser import ArgParser
from gen.lib import Person
from cli.grampscli import get_remote_interface
from BasicUtils import name_displayer

class get_person_cursor:
    def __len__(self):
        return len(gapi.dbstate.db.person_map)
    def __enter__(self):
        for gname, name, handle in gapi.dbstate.db.sorted:
            yield handle, gapi.dbstate.db.person_map[handle]
    def __exit__(self, *args, **kwargs):
        pass

def get_familytrees():
    summary_list = gapi.arghandler.dbman.family_tree_summary()
    return [summary["Family tree"] for summary in summary_list]

def get_summary():
    dbfile = gapi.dbstate.db.full_name
    summary_list = gapi.arghandler.dbman.family_tree_summary()
    return [summary for summary in summary_list if summary["Path"] == dbfile][0]

argpars = ArgParser(["gramps.py", "-O", GRAMPS_DATABASE, "--force-unlock"])
gapi = get_remote_interface(argpars)
print "GRAMPS database \"%s\" loading..." % GRAMPS_DATABASE
_NAME_COL   = 3
ngn = name_displayer.name_grouping_data
nsn = name_displayer.raw_sorted_name
gapi.dbstate.db.sorted = []
with gapi.dbstate.db.get_person_cursor() as cursor:
    for handle, data in cursor:
        name_data = data[_NAME_COL]
        group_name = ngn(gapi.dbstate.db, name_data)
        sorted_name = nsn(name_data)
        # (u'Cooper', u'Cooper, Elizabeth Ann', 'b2cfa6c5c41642f8f79',)
        gapi.dbstate.db.sorted.append( (group_name, sorted_name, handle) )
gapi.dbstate.db.sorted.sort()
gapi.dbstate.db.get_person_cursor = get_person_cursor
gapi.dbstate.db.summary = get_summary()

