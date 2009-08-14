from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from gen.lib.date import Date as GDate
from gen.lib.date import Today as Now
from Utils import create_id, create_uid

## Type tables are initially filled with their core values in init.py
## which is run by make.

### START GRAMPS TYPES  
def get_datamap(grampsclass):
    return [(x[0],x[2]) for x in grampsclass._DATAMAP]

class mGrampsType(models.Model):
    """
    The abstract base class for all types. 
    Types are enumerated integers. One integer corresponds with custom, then 
    custom_type holds the type name
    """
    class Meta: abstract = True

    _CUSTOM = 0
    _DEFAULT = 0
    _DATAMAP = []

    custom_name = models.CharField(max_length=40, blank=True)
    
    def __unicode__(self): return self.custom_name

class MarkerType(mGrampsType):
    from gen.lib.markertype import MarkerType
    _DATAMAP = get_datamap(MarkerType)
    val = models.IntegerField('marker', choices=_DATAMAP, blank=False)

class NameType(mGrampsType):
    from gen.lib.nametype import NameType
    _DATAMAP = get_datamap(NameType)
    val = models.IntegerField('name type', choices=_DATAMAP, blank=False)

class AttributeType(mGrampsType):
    from gen.lib.attrtype import AttributeType
    _DATAMAP = get_datamap(AttributeType)
    val = models.IntegerField('attribute type', choices=_DATAMAP, blank=False)

class UrlType(mGrampsType):
    from gen.lib.urltype import UrlType
    _DATAMAP = get_datamap(UrlType)
    val = models.IntegerField('url type', choices=_DATAMAP, blank=False)

class ChildRefType(mGrampsType):
    from gen.lib.childreftype import ChildRefType
    _DATAMAP = get_datamap(ChildRefType)
    val = models.IntegerField('child reference type', choices=_DATAMAP, blank=False)

class RepositoryType(mGrampsType):
    from gen.lib.repotype import RepositoryType
    _DATAMAP = get_datamap(RepositoryType)
    val = models.IntegerField('repository type', choices=_DATAMAP, blank=False)

class EventType(mGrampsType):
    from gen.lib.eventtype import EventType
    _DATAMAP = get_datamap(EventType)
    val = models.IntegerField('event type', choices=_DATAMAP, blank=False)

class FamilyRelType(mGrampsType):
    from gen.lib.familyreltype import FamilyRelType
    _DATAMAP = get_datamap(FamilyRelType)
    val = models.IntegerField('family relation type', choices=_DATAMAP, blank=False)

class SourceMediaType(mGrampsType):
    from gen.lib.srcmediatype import SourceMediaType
    _DATAMAP = get_datamap(SourceMediaType)
    val = models.IntegerField('source medium type', choices=_DATAMAP, blank=False)

class EventRoleType(mGrampsType):
    from gen.lib.eventroletype import EventRoleType
    _DATAMAP = get_datamap(EventRoleType)
    val = models.IntegerField('event role type', choices=_DATAMAP, blank=False)

class NoteType(mGrampsType):
    from gen.lib.notetype import NoteType
    _DATAMAP = get_datamap(NoteType)
    val = models.IntegerField('note type', choices=_DATAMAP, blank=False)

class MarkupType(mGrampsType):
    _DATAMAP = [] ## What is this type?
    val = models.IntegerField('markup type', choices=_DATAMAP, blank=False)

class FamilyType(mGrampsType):
    _DATAMAP = [] ## What is this type?
    val = models.IntegerField('family type', choices=_DATAMAP, blank=False)

class RepoType(mGrampsType):
    _DATAMAP = [] ## What is this type?
    val = models.IntegerField('repository type', choices=_DATAMAP, blank=False)

### END GRAMPS TYPES 

#--------------------------------------------------------------------------------
#
# Misc Tables
#
#--------------------------------------------------------------------------------

class DateObject(models.Model):
    class Meta: abstract = True

    calendar = models.IntegerField()
    modifier = models.IntegerField()
    quality = models.IntegerField()
    day1 = models.IntegerField()
    month1 = models.IntegerField()
    year1 = models.IntegerField()
    slash1 = models.BooleanField()
    day2 = models.IntegerField(blank=True)
    month2 = models.IntegerField(blank=True)
    year2 = models.IntegerField(blank=True)
    slash2 = models.BooleanField(blank=True)
    text = models.CharField(max_length=80, blank=True)
    sortval = models.IntegerField()
    newyear = models.IntegerField()

    def set_date_from_datetime(self, date_time, text=""):
        """
        Sets Date fields from an object that has year, month, and day
        properties.
        """
        y, m, d = date_time.year, date_time.month, date_time.day
        self.set_ymd(self, y, m, d, text=text)

    def set_date_from_ymd(self, y, m, d, text=""):
        """
        Sets Date fields from a year, month, and day.
        """
        gdate = GDate(y, m, d)
        gdate.text = text
        self.set_date_from_gdate(gdate)

    def set_date_from_gdate(self, gdate):
        """
        Sets Date fields from a Gramps date object.
        """
        (self.calendar, self.modifier, self.quality, dateval, self.text, 
         self.sortval, self.newyear) = gdate.serialize()
        if dateval is None:
            (self.day1, self.month1, self.year1, self.slash1) = 0, 0, 0, False
            (self.day2, self.month2, self.year2, self.slash2) = 0, 0, 0, False
        elif len(dateval) == 8:
            (self.day1, self.month1, self.year1, self.slash1, 
             self.day2, self.month2, self.year2, self.slash2) = dateval
        elif len(dateval) == 4:
            (self.day1, self.month1, self.year1, self.slash1) = dateval
            (self.day2, self.month2, self.year2, self.slash2) = 0, 0, 0, False

class Name(DateObject, models.Model):
    person = models.ForeignKey('Person')
    order = models.PositiveIntegerField()
    primary_name = models.BooleanField('primary')
    private = models.BooleanField('private')
    first_name = models.TextField(blank=True)
    surname = models.TextField(blank=True)
    suffix = models.TextField(blank=True)
    title = models.TextField(blank=True)
    prefix = models.TextField(blank=True)
    patronymic = models.TextField(blank=True)
    call = models.TextField(blank=True)
    group_as = models.TextField(blank=True)
    sort_as = models.IntegerField(blank=True)
    display_as = models.IntegerField(blank=True)

class Address(models.Model):
    private = models.BooleanField()

## location
## attribute
## url
## datamap

#--------------------------------------------------------------------------------
#
# Primary Tables
#
#--------------------------------------------------------------------------------

class PrimaryObject(models.Model):
    """
    Common attribute of all primary objects with key on the handle
    """
    class Meta: abstract = True

    handle = models.CharField(max_length=19, primary_key=True, unique=True)
    gramps_id =  models.CharField('gramps id', max_length=25, blank=True)
    marker = models.ForeignKey(MarkerType, blank=False)
    change = models.DateTimeField('last changed')
    private = models.BooleanField('private')

    def __unicode__(self): return self.gramps_id 

class Event(PrimaryObject, DateObject):
    event_type = models.ForeignKey(EventType)
    description = models.CharField('description', max_length=50, blank=True)

class Note(PrimaryObject):
    note_type = models.ForeignKey(NoteType)
    text  = models.TextField(blank=True)
    format = models.IntegerField('format', blank=True)

class Source(PrimaryObject):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    pubinfo = models.CharField(max_length=50)
    abbrev = models.CharField(max_length=50)

class Place(PrimaryObject):
    title = models.TextField()
    main_location = models.CharField(max_length=25)
    long = models.TextField()
    lat = models.TextField()

class Media(PrimaryObject):
    path = models.TextField()
    mime = models.TextField()
    desc = models.TextField()

class Repository(PrimaryObject):
    repo_type = models.ForeignKey(RepoType)
    name = models.TextField()

#--------------------------------------------------------------------------------
#
# Reference Objects
#
#--------------------------------------------------------------------------------

class BaseRef(models.Model):
    class Meta: abstract = True

    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey("object_type", "object_id")
    private = models.BooleanField()
  
class NoteRef(BaseRef):
    note = models.ForeignKey(Note)

    def __unicode__(self):
        return "NoteRef to " + str(self.object)

class SourceRef(BaseRef, DateObject):
    page = models.CharField(max_length=50)
    source = models.ForeignKey(Source)
    confidence = models.IntegerField()

    def __unicode__(self):
        return "SourceRef to " + str(self.object)

class EventRef(BaseRef):
    role_type = models.ForeignKey(EventRoleType)

    def __unicode__(self):
        return "EventRef to " + str(self.object)

class RepositoryRef(BaseRef):
    source_media_type = models.ForeignKey(SourceMediaType)
    call_number = models.CharField(max_length=50)

    def __unicode__(self):
        return "RepositoryRef to " + str(self.object)

class PersonRef(BaseRef):
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return "PersonRef to " + str(self.object)

class ChildRef(BaseRef):
    father_rel_type = models.ForeignKey(FamilyRelType, related_name="father_ref")
    mother_rel_type = models.ForeignKey(FamilyRelType, related_name="mother_ref")

    def __unicode__(self):
        return "ChildRef to " + str(self.object)

class MediaRef(BaseRef):
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()

    def __unicode__(self):
        return "MediaRef to " + str(self.object)

#--------------------------------------------------------------------------------
#
# Primary tables that mention other objects
#
#--------------------------------------------------------------------------------

class Person(PrimaryObject):
    """
    The model for the person object
    """
    GENDERMAP = [(2, 'Unknown'), (1, 'Male'), (0, 'Female')]
    gender = models.IntegerField(blank=False, choices=GENDERMAP)

class Family(PrimaryObject):
    father = models.ForeignKey(Person, related_name="father_ref", blank=True)
    mother = models.ForeignKey(Person, related_name="mother_ref", blank=True)
    family_type = models.ForeignKey(FamilyType)


#--------------------------------------------------------------------------------
#
# Misc tables that mention other objects
#
#--------------------------------------------------------------------------------

class Lds(models.Model):
    lds_type = models.IntegerField()
    place = models.ForeignKey(Place)
    famc = models.ForeignKey(Family)
    temple = models.TextField()
    status = models.IntegerField()
    private = models.BooleanField()

class Markup(models.Model):
    markup_type = models.ForeignKey(MarkupType)
    value = models.TextField()
    start_stop_list = models.TextField()

def main():
    m1 = MarkerType(val=0)
    m1.save()
    p1 = Person(handle=create_id(), marker=m1, change=Now())
    p1.gender = 2
    p1.save()
    n1 = Name()
    e1 = Event(handle=create_id())
    e1.set_date_from_gdate( GDate("between September 1, 1962 and 1963") )
    return e1

if __name__ == "__main__":
    e1 = main()
