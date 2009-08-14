import sys
import os

sys.path.append("../../src")
from gen.lib.markertype import MarkerType
from gen.lib.nametype import NameType
from gen.lib.attrtype import AttributeType
from gen.lib.urltype import UrlType
from gen.lib.childreftype import ChildRefType
from gen.lib.repotype import RepositoryType
from gen.lib.eventtype import EventType
from gen.lib.familyreltype import FamilyRelType
from gen.lib.srcmediatype import SourceMediaType
from gen.lib.eventroletype import EventRoleType
from gen.lib.notetype import NoteType

def get_datamap(x):
    return (x[0],x[2])

print "["
count = 1
for name,constr in [("Person", "Person", ), 
                    ("Event", "Event", ),
                    ("Family", "Family", ),
                    ("Place", "Place", ),
                    ("Source", "Source", ),
                    ("Media", "MediaObject", ),
                    ("Repository", "Repository", ),
                    ("Note", "Note", ),
                    ]:
    print "   {"
    print "      \"model\": \"views.%s\"," % "view"
    print "      \"pk\": %d," % count
    print "      \"fields\":"
    print "         {"
    print "            \"name\"   : \"%s\"," % name
    print "            \"constructor\": \"%s\"" % constr
    print "         }"
    print "   },"
    count += 1

for type in [MarkerType, NameType, AttributeType, UrlType, ChildRefType, 
             RepositoryType, EventType, FamilyRelType, SourceMediaType, 
             EventRoleType, NoteType]:
    count = 1
    for tuple in type._DATAMAP:
        val, name = get_datamap(tuple)
        print "   {"
        print "      \"model\": \"tables.%s\"," % type.__name__.lower()
        print "      \"pk\": %d," % count
        print "      \"fields\":"
        print "         {"
        print "            \"val\"   : %d," % val
        print "            \"custom_name\": \"%s\"" % name
        print "         }"
        print "   }",
        if type == NoteType and count == len(type._DATAMAP):
            print
        else:
            print ","
        count += 1
print "]"
