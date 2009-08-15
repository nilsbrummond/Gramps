from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from gen.lib.date import Date as GDate, Today
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

    name = models.CharField(max_length=40, blank=True)
    
    def __unicode__(self): return self.name

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

class GenderType(mGrampsType):
    _DATAMAP = [(2, 'Unknown'), (1, 'Male'), (0, 'Female')]
    val = models.IntegerField('gender type', choices=_DATAMAP, blank=False)

### END GRAMPS TYPES 

#--------------------------------------------------------------------------------
#
# Support definitions
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
    day2 = models.IntegerField(blank=True, null=True)
    month2 = models.IntegerField(blank=True, null=True)
    year2 = models.IntegerField(blank=True, null=True)
    slash2 = models.BooleanField(blank=True, null=True)
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

    ## Fields:
    id = models.AutoField(primary_key=True)
    handle = models.CharField(max_length=19, unique=True)
    gramps_id =  models.CharField('gramps id', max_length=25, blank=True)
    last_changed = models.DateTimeField('last changed', auto_now=True)
    private = models.BooleanField('private')
    ## Keys:
    marker_type = models.ForeignKey('MarkerType')

    def __unicode__(self): return self.gramps_id 

class Person(PrimaryObject):
    """
    The model for the person object
    """
    gender_type = models.ForeignKey('GenderType')

class Family(PrimaryObject):
    father = models.ForeignKey('Person', related_name="father_ref", null=True, blank=True)
    mother = models.ForeignKey('Person', related_name="mother_ref", null=True, blank=True)
    family_rel_type = models.ForeignKey('FamilyRelType')
    children = models.ManyToManyField('Person')

class Source(PrimaryObject):
    title = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=50, blank=True)
    pubinfo = models.CharField(max_length=50, blank=True)
    abbrev = models.CharField(max_length=50, blank=True)
    references = generic.GenericRelation('SourceRef', related_name="refs")

class Event(DateObject, PrimaryObject):
    event_type = models.ForeignKey('EventType')
    description = models.CharField('description', max_length=50, blank=True)
    references = generic.GenericRelation('EventRef', related_name="refs")

class Repository(PrimaryObject):
    repository_type = models.ForeignKey('RepositoryType')
    name = models.TextField(blank=True)
    references = generic.GenericRelation('RepositoryRef', related_name="refs")

class Place(PrimaryObject):
    title = models.TextField(blank=True)
    main_location = models.CharField(max_length=25, blank=True)
    long = models.TextField(blank=True)
    lat = models.TextField(blank=True)

class Media(PrimaryObject):
    path = models.TextField(blank=True)
    mime = models.TextField(blank=True)
    desc = models.TextField(blank=True)
    references = generic.GenericRelation('MediaRef', related_name="refs")

class Note(PrimaryObject):
    note_type = models.ForeignKey('NoteType')
    text  = models.TextField(blank=True)
    preformatted = models.BooleanField('preformatted')
    #references = generic.GenericRelation('NoteRef', related_name="refs")

#--------------------------------------------------------------------------------
#
# Secondary Tables
#
#--------------------------------------------------------------------------------

class SecondaryObject(models.Model):
    """
    We use interlinked objects, secondary object is the table for primary 
    objects to refer to when linking to non primary objects
    """
    class Meta: abstract = True

    private = models.BooleanField()
    last_changed = models.DateTimeField('last changed', auto_now=True)

class Name(DateObject, SecondaryObject):
    order = models.PositiveIntegerField()
    primary_name = models.BooleanField('primary')
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

    person = models.ForeignKey('Person')

class Lds(SecondaryObject):
    """
    BAPTISM         = 0
    ENDOWMENT       = 1
    SEAL_TO_PARENTS = 2
    SEAL_TO_SPOUSE  = 3
    CONFIRMATION    = 4
    
    DEFAULT_TYPE = BAPTISM


    STATUS_NONE      = 0
    STATUS_BIC       = 1
    STATUS_CANCELED  = 2
    STATUS_CHILD     = 3
    STATUS_CLEARED   = 4
    STATUS_COMPLETED = 5
    STATUS_DNS       = 6
    STATUS_INFANT    = 7
    STATUS_PRE_1970  = 8
    STATUS_QUALIFIED = 9
    STATUS_DNS_CAN   = 10
    STATUS_STILLBORN = 11
    STATUS_SUBMITTED = 12
    STATUS_UNCLEARED = 13

    DEFAULT_STATUS = STATUS_NONE
    """
    lds_type = models.IntegerField() # FIXME
    place = models.ForeignKey('Place')
    famc = models.ForeignKey('Family')
    temple = models.TextField(blank=True)
    status = models.IntegerField() # FIXME

class Markup(models.Model):
    note = models.ForeignKey('Note')
    order = models.PositiveIntegerField()
    string = models.TextField(blank=True)
    start_stop_list = models.TextField(default="[]")

class Address(DateObject, SecondaryObject):
    location = models.OneToOneField('Location')

class Location(models.Model):
    street = models.TextField(blank=True)
    city = models.TextField(blank=True)
    county = models.TextField(blank=True)
    state = models.TextField(blank=True)
    country = models.TextField(blank=True)
    postal = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    parish = models.TextField(blank=True)

## location
## attribute
## url models.URLField
## datamap

#--------------------------------------------------------------------------------
#
# Reference Objects
#
#--------------------------------------------------------------------------------

class BaseRef(models.Model):
    class Meta: abstract = True

    object_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    referenced_by = generic.GenericForeignKey("object_type", "object_id")

    last_changed = models.DateTimeField('last changed', auto_now=True)
    private = models.BooleanField()
  
class NoteRef(BaseRef):
    note = models.ForeignKey('Note') 

    def __unicode__(self):
        return "NoteRef from " + str(self.referenced_by)

class SourceRef(DateObject, BaseRef):
    page = models.CharField(max_length=50)
    confidence = models.IntegerField()
    source = models.ForeignKey('Source')

    def __unicode__(self):
        return "SourceRef to " + str(self.source)

class EventRef(BaseRef):
    role_type = models.ForeignKey('EventRoleType')
    event = models.ForeignKey('Event')

    def __unicode__(self):
        return "EventRef to " + str(self.event)

class RepositoryRef(BaseRef):
    source_media_type = models.ForeignKey('SourceMediaType')
    call_number = models.CharField(max_length=50)
    repository = models.ForeignKey('Repository')

    def __unicode__(self):
        return "RepositoryRef to " + str(self.repository)

class PersonRef(BaseRef):
    description = models.CharField(max_length=50)
    person = models.ForeignKey('Person')

    def __unicode__(self):
        return "PersonRef to " + str(self.person)

class ChildRef(BaseRef):
    father_rel_type = models.ForeignKey('FamilyRelType', related_name="father_rel")
    mother_rel_type = models.ForeignKey('FamilyRelType', related_name="mother_rel")
    child = models.ForeignKey('Person')

    def __unicode__(self):
        return "ChildRef to " + str(self.child)

class MediaRef(BaseRef):
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    media = models.ForeignKey('Media')

    def __unicode__(self):
        return "MediaRef to " + str(self.media)

#--------------------------------------------------------------------------------
#
# Testing Functions
#
#--------------------------------------------------------------------------------

## Primary:

def test_Person():
    m = MarkerType.objects.get(name="")
    p = Person(handle=create_id(), marker_type=m)
    p.gender_type = GenderType.objects.get(name="Unknown") 
    p.save()
    return p

def test_Family():
    m = MarkerType.objects.get(name="")
    frt = FamilyRelType.objects.get(name="Unknown")
    f = Family(handle=create_id(), marker_type=m, family_rel_type=frt)
    f.save()
    return f

def test_Source():
    m = MarkerType.objects.get(name="")
    s = Source(handle=create_id(), marker_type=m)
    s.save()
    s.gramps_id = "S%04d" % s.id
    s.save()
    return s

def test_Event():
    m = MarkerType.objects.get(name="")
    et = EventType.objects.get(name="Unknown")
    e = Event(handle=create_id(), marker_type=m, event_type=et)
    e.set_date_from_gdate( GDate() )
    e.save()
    return e

def test_Repository():
    m = MarkerType.objects.get(name="")
    rt = RepositoryType.objects.get(name="Unknown")
    r = Repository(handle=create_id(), marker_type=m, repository_type=rt)
    r.save()
    return r

def test_Place():
    m = MarkerType.objects.get(name="")
    p = Place(handle=create_id(), marker_type=m)
    p.save()
    return p
    
def test_Media():
    m = MarkerType.objects.get(name="")
    media = Media(handle=create_id(), marker_type=m)
    media.save()
    return media

def test_Note():
    m = MarkerType.objects.get(name="")
    note_type = NoteType.objects.get(name="Unknown")
    note = Note(handle=create_id(), marker_type=m, note_type=note_type, 
                preformatted=False)
    note.save()
    return note

def test_Family_with_children():
    father = test_Person()
    fname = test_Name(father, "Blank", "Lowell")
    mother = test_Person()
    mname = test_Name(mother, "Bamford", "Norma")
    family_rel_type = FamilyRelType.objects.get(name="Married")
    m = MarkerType.objects.get(name="")
    f = Family(handle=create_id(), father=father, mother=mother, 
               family_rel_type=family_rel_type, marker_type=m)
    f.save()
    for names in [("Blank", "Doug"), ("Blank", "Laura"), ("Blank", "David")]:
        p = test_Person()
        n = test_Name(p, names[0], names[1])
        f.children.add(p)
    f.save()
    return f

## Secondary:

def test_Name(person=None, surname=None, first=None):
    if not person: # Testing
        person = test_Person()
    m = MarkerType.objects.get(name="")
    n = Name(person=person)
    if first:
        n.first_name = first
    if surname:
        n.surname = surname
    n.set_date_from_gdate(Today())
    n.order = 1
    n.sort_as = 1
    n.display_as = 1
    n.save()
    person.save()
    return n

def test_Markup(note=None):
    if not note:
        note = test_Note()
    markup = Markup(note=note)
    markup.order = 1
    markup.save()
    return markup

def test_Lds(place=None, famc=None):
    if not place:
        place = test_Place()
    if not famc:
        famc = test_Family()
    lds = Lds(lds_type=0, status=0, place=place, famc=famc)
    lds.save()
    return lds
    
def test_NoteRef():
    note = test_Note()
    person = test_Person()
    note_ref = NoteRef(referenced_by=person, note=note)
    note_ref.save()
    family = test_Family()
    note_ref = NoteRef(referenced_by=family, note=note)
    note_ref.save()
    return note_ref

def test_SourceRef():
    note = test_Note()
    source = test_Source()
    source_ref = SourceRef(referenced_by=note, source=source, confidence=4)
    source_ref.set_date_from_gdate(Today())
    source_ref.save()
    return source_ref

#--------------------------------------------------------------------------------
#
# Testing
#
#--------------------------------------------------------------------------------

def main():
    for test_Item in [test_Person, test_Family, test_Family_with_children, 
                      test_Source, test_Event, 
                      test_Repository, test_Place, test_Media, test_Note, 
                      test_Name, test_Markup, test_Lds, test_NoteRef,
                      test_SourceRef]:
        print "testing:", test_Item.__name__
        obj = test_Item()

if __name__ == "__main__":
    main()
