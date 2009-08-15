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
    handle = models.CharField(max_length=19, primary_key=True, unique=True)
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
    references = generic.GenericRelation('PersonRef', related_name="refs")

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

class Event(PrimaryObject, DateObject):
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
    references = generic.GenericRelation('NoteRef', related_name="refs")

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

class Address(SecondaryObject):
    pass

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
    content = generic.GenericForeignKey("object_type", "object_id")
    last_changed = models.DateTimeField('last changed', auto_now=True)
    private = models.BooleanField()
  
class NoteRef(BaseRef):
    note = models.OneToOneField('Note')

    def __unicode__(self):
        return "NoteRef to " + str(self.object)

class SourceRef(BaseRef, DateObject):
    page = models.CharField(max_length=50)
    confidence = models.IntegerField()
    source = models.OneToOneField('Source')

    def __unicode__(self):
        return "SourceRef to " + str(self.object)

class EventRef(BaseRef):
    role_type = models.ForeignKey('EventRoleType')
    event = models.OneToOneField('Event')

    def __unicode__(self):
        return "EventRef to " + str(self.object)

class RepositoryRef(BaseRef):
    source_media_type = models.ForeignKey('SourceMediaType')
    call_number = models.CharField(max_length=50)
    repository = models.OneToOneField('Repository')

    def __unicode__(self):
        return "RepositoryRef to " + str(self.object)

class PersonRef(BaseRef):
    description = models.CharField(max_length=50)
    person = models.OneToOneField('Person')

    def __unicode__(self):
        return "PersonRef to " + str(self.object)

class ChildRef(BaseRef):
    father_rel_type = models.ForeignKey('FamilyRelType', related_name="father_rel")
    mother_rel_type = models.ForeignKey('FamilyRelType', related_name="mother_rel")
    child = models.OneToOneField('Person')

    def __unicode__(self):
        return "ChildRef to " + str(self.object)

class MediaRef(BaseRef):
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    media = models.OneToOneField('Media')

    def __unicode__(self):
        return "MediaRef to " + str(self.object)

#--------------------------------------------------------------------------------
#
# Testing Functions
#
#--------------------------------------------------------------------------------

## Primary:

def new_Person():
    m = MarkerType.objects.get(name="")
    p = Person(handle=create_id(), marker_type=m)
    p.gender_type = GenderType.objects.get(name="Unknown") 
    p.save()
    return p

def new_Family():
    m = MarkerType.objects.get(name="")
    frt = FamilyRelType.objects.get(name="Unknown")
    f = Family(handle=create_id(), marker_type=m, family_rel_type=frt)
    f.save()
    return f

def new_Source():
    m = MarkerType.objects.get(name="")
    s = Source(handle=create_id(), marker_type=m)
    s.save()
    return s

def new_Event():
    m = MarkerType.objects.get(name="")
    et = EventType.objects.get(name="Unknown")
    e = Event(handle=create_id(), marker_type=m, event_type=et)
    e.set_date_from_gdate( GDate() )
    e.save()
    return e

def new_Repository():
    m = MarkerType.objects.get(name="")
    rt = RepositoryType.objects.get(name="Unknown")
    r = Repository(handle=create_id(), marker_type=m, repository_type=rt)
    r.save()
    return r

def new_Place():
    m = MarkerType.objects.get(name="")
    p = Place(handle=create_id(), marker_type=m)
    p.save()
    return p
    
def new_Media():
    m = MarkerType.objects.get(name="")
    media = Media(handle=create_id(), marker_type=m)
    media.save()
    return media

def new_Note():
    m = MarkerType.objects.get(name="")
    note_type = NoteType.objects.get(name="Unknown")
    note = Note(handle=create_id(), marker_type=m, note_type=note_type, 
                preformatted=False)
    note.save()
    return note

def new_Family():
    father = new_Person()
    fname = new_Name(father, "Blank", "Lowell")
    mother = new_Person()
    mname = new_Name(mother, "Bamford", "Norma")
    family_rel_type = FamilyRelType.objects.get(name="Married")
    m = MarkerType.objects.get(name="")
    f = Family(handle=create_id(), father=father, mother=mother, 
               family_rel_type=family_rel_type, marker_type=m)
    for names in [("Blank", "Doug"), ("Blank", "Laura"), ("Blank", "David")]:
        p = new_Person()
        n = new_Name(p, names[0], names[1])
        f.children.add(p)
    f.save()
    return f

## Secondary:

def new_Name(person=None, surname=None, first=None):
    if not person: # Testing
        person = new_Person()
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

def new_Markup(note=None):
    if not note:
        note = new_Note()
    markup = Markup(note=note)
    markup.order = 1
    markup.save()
    return markup

def new_Lds(place=None, famc=None):
    if not place:
        place = new_Place()
    if not famc:
        famc = new_Family()
    lds = Lds(lds_type=0, status=0, place=place, famc=famc)
    lds.save()
    return lds
    
def new_NoteRef():
    note = new_Note()
    person = new_Person()
    family = new_Family()
    #note_ref = NoteRef(content=person, note=note)
    #note_ref.save()
    #note_ref = NoteRef(referenced_by=family, note=note)
    #note_ref.save()
    #return note_ref

def new_SourceRef():
    note = new_Note()
    source = new_Source()
    source_ref = SourceRef(content=note, source=source)
    source_ref.save()
    return source_ref

#--------------------------------------------------------------------------------
#
# Testing
#
#--------------------------------------------------------------------------------

def main():
    for new_Item in [new_Person, new_Family, new_Source, new_Event, new_Repository,
                     new_Place, new_Media, new_Note, new_Name, new_Markup, new_Lds,
                     new_NoteRef]:
        print new_Item.__name__
        obj = new_Item()

if __name__ == "__main__":
    main()
