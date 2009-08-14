"""
Creates a JSON representation of data for Django's fixture
architecture. We could have done this in Python, or SQL, 
but this makes it useful for all Django-based backends
but still puts it into their syncdb API.
"""

import sys

import settings

sys.path.append(settings.GRAMPS_PATH) # add gramps to path
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

from tables.models import GenderType

def get_datamap(x):
    """
    Returns (code, Name) for a Gramps type tuple.
    """
    return (x[0],x[2])

## Add the data for the Views:

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

## Add the data for the type models:

type_models = [MarkerType, NameType, AttributeType, UrlType, ChildRefType, 
               RepositoryType, EventType, FamilyRelType, SourceMediaType, 
               EventRoleType, NoteType, GenderType]
for type in type_models:
    count = 1
    # Add each code:
    for tuple in type._DATAMAP:
        if len(tuple) == 3: # GRAMPS BSDDB style
            val, name = get_datamap(tuple)
        else: # NEW SQL based
            val, name = tuple
        print "   {"
        print "      \"model\": \"tables.%s\"," % type.__name__.lower()
        print "      \"pk\": %d," % count
        print "      \"fields\":"
        print "         {"
        print "            \"val\"   : %d," % val
        print "            \"name\": \"%s\"" % name
        print "         }"
        print "   }",
        # if it is the last one of the last one, no comma
        if type == type_models[-1] and count == len(type._DATAMAP):
            print
        else:
            print ","
        count += 1
print "]"
