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

    name = models.CharField(max_length=40)
    
    def __unicode__(self): return self.name

    def get_default(self):
        """ return a tuple default (val,name) """
        return self._DATAMAP[self._DEFAULT]

class MarkerType(mGrampsType):
    from gen.lib.markertype import MarkerType
    _DATAMAP = get_datamap(MarkerType)
    _CUSTOM = MarkerType._CUSTOM
    _DEFAULT = _DATAMAP[MarkerType._DEFAULT]
    val = models.IntegerField('marker', choices=_DATAMAP, blank=False)

class NameType(mGrampsType):
    from gen.lib.nametype import NameType
    _DATAMAP = get_datamap(NameType)
    _CUSTOM = NameType._CUSTOM
    _DEFAULT = _DATAMAP[NameType._DEFAULT]
    val = models.IntegerField('name type', choices=_DATAMAP, blank=False)

class AttributeType(mGrampsType):
    from gen.lib.attrtype import AttributeType
    _DATAMAP = get_datamap(AttributeType)
    _CUSTOM = AttributeType._CUSTOM
    _DEFAULT = _DATAMAP[AttributeType._DEFAULT]
    val = models.IntegerField('attribute type', choices=_DATAMAP, blank=False)

class UrlType(mGrampsType):
    from gen.lib.urltype import UrlType
    _DATAMAP = get_datamap(UrlType)
    _CUSTOM = UrlType._CUSTOM
    _DEFAULT = _DATAMAP[UrlType._DEFAULT]
    val = models.IntegerField('url type', choices=_DATAMAP, blank=False)

class ChildRefType(mGrampsType):
    from gen.lib.childreftype import ChildRefType
    _DATAMAP = get_datamap(ChildRefType)
    _CUSTOM = ChildRefType._CUSTOM
    _DEFAULT = _DATAMAP[ChildRefType._DEFAULT]
    val = models.IntegerField('child reference type', choices=_DATAMAP, blank=False)

class RepositoryType(mGrampsType):
    from gen.lib.repotype import RepositoryType
    _DATAMAP = get_datamap(RepositoryType)
    _CUSTOM = RepositoryType._CUSTOM
    _DEFAULT = _DATAMAP[RepositoryType._DEFAULT]
    val = models.IntegerField('repository type', choices=_DATAMAP, blank=False)

class EventType(mGrampsType):
    from gen.lib.eventtype import EventType
    _DATAMAP = get_datamap(EventType)
    _CUSTOM = EventType._CUSTOM
    _DEFAULT = _DATAMAP[EventType._DEFAULT]
    val = models.IntegerField('event type', choices=_DATAMAP, blank=False)

class FamilyRelType(mGrampsType):
    from gen.lib.familyreltype import FamilyRelType
    _DATAMAP = get_datamap(FamilyRelType)
    _CUSTOM = FamilyRelType._CUSTOM
    _DEFAULT = _DATAMAP[FamilyRelType._DEFAULT]
    val = models.IntegerField('family relation type', choices=_DATAMAP, blank=False)

class SourceMediaType(mGrampsType):
    from gen.lib.srcmediatype import SourceMediaType
    _DATAMAP = get_datamap(SourceMediaType)
    _CUSTOM = SourceMediaType._CUSTOM
    _DEFAULT = _DATAMAP[SourceMediaType._DEFAULT]
    val = models.IntegerField('source medium type', choices=_DATAMAP, blank=False)

class EventRoleType(mGrampsType):
    from gen.lib.eventroletype import EventRoleType
    _DATAMAP = get_datamap(EventRoleType)
    _CUSTOM = EventRoleType._CUSTOM
    _DEFAULT = _DATAMAP[EventRoleType._DEFAULT]
    val = models.IntegerField('event role type', choices=_DATAMAP, blank=False)

class NoteType(mGrampsType):
    from gen.lib.notetype import NoteType
    _DATAMAP = get_datamap(NoteType)
    _CUSTOM = NoteType._CUSTOM
    _DEFAULT = _DATAMAP[NoteType._DEFAULT]
    val = models.IntegerField('note type', choices=_DATAMAP, blank=False)

class GenderType(mGrampsType):
    _DATAMAP = [(2, 'Unknown'), (1, 'Male'), (0, 'Female')]
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('gender type', choices=_DATAMAP, blank=False)

class LdsType(mGrampsType):
    _DATAMAP = [(0, "Baptism"        ),
                (1, "Endowment"      ),
                (2, "Seal to Parents"),
                (3, "Seal to Spouse"),
                (4, "Confirmation")]
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('lds type', choices=_DATAMAP, blank=False)

class LdsStatus(mGrampsType):
    _DATAMAP = [(0, "None"),
                (1, "BIC"), 
                (2, "Canceled"),
                (3, "Child"),
                (4, "Cleared"),
                (5, "Completed"),
                (6, "Dns"),
                (7, "Infant"),
                (8, "Pre 1970"),
                (9, "Qualified"),
                (10, "DNSCAN"),
                (11, "Stillborn"),
                (12, "Submitted"),
                (13, "Uncleared")]
    _DEFAULT = _DATAMAP[0]
    val = models.IntegerField('lds status', choices=_DATAMAP, blank=False)


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

class Config(models.Model):
    db_version = models.CharField(max_length=25)
    created = models.DateTimeField('date/time created')

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
    names = models.ManyToManyField('Name', null=True)
    families = models.ManyToManyField('Family', null=True)
    parent_families = models.ManyToManyField('Family', related_name="parent_families")
    addresses = models.ManyToManyField('Address', null=True)
    references = generic.GenericRelation('PersonRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

class Family(PrimaryObject):
    father = models.ForeignKey('Person', related_name="father_ref", 
                               null=True, blank=True)
    mother = models.ForeignKey('Person', related_name="mother_ref", 
                               null=True, blank=True)
    family_rel_type = models.ForeignKey('FamilyRelType')

class Source(PrimaryObject):
    title = models.CharField(max_length=50, blank=True)
    author = models.CharField(max_length=50, blank=True)
    pubinfo = models.CharField(max_length=50, blank=True)
    abbrev = models.CharField(max_length=50, blank=True)
    references = generic.GenericRelation('SourceRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

class Event(DateObject, PrimaryObject):
    event_type = models.ForeignKey('EventType')
    description = models.CharField('description', max_length=50, blank=True)
    place = models.ForeignKey('Place', null=True)
    references = generic.GenericRelation('EventRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

class Repository(PrimaryObject):
    repository_type = models.ForeignKey('RepositoryType')
    name = models.TextField(blank=True)
    addresses = models.ManyToManyField('Address', null=True)
    references = generic.GenericRelation('RepositoryRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

class Place(PrimaryObject):
    title = models.TextField(blank=True)
    locations = models.ManyToManyField('Location', null=True)
    long = models.TextField(blank=True)
    lat = models.TextField(blank=True)

class Media(PrimaryObject):
    path = models.TextField(blank=True)
    mime = models.TextField(blank=True)
    desc = models.TextField(blank=True)
    references = generic.GenericRelation('MediaRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

class Note(PrimaryObject):
    note_type = models.ForeignKey('NoteType')
    text  = models.TextField(blank=True)
    preformatted = models.BooleanField('preformatted')
    references = generic.GenericRelation('NoteRef', related_name="refs",
                                         content_type_field="object_type",
                                         object_id_field="object_id")

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
    name_type = models.ForeignKey('NameType', related_name="name_code")
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

    def __unicode__(self):
        return self.surname + ", " + self.first_name

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
    lds_type = models.ForeignKey('LdsType')
    place = models.ForeignKey('Place', null=True)
    famc = models.ForeignKey('Family', null=True)
    temple = models.TextField(blank=True)
    status = models.ForeignKey('LdsStatus') 

class Markup(models.Model):
    note = models.ForeignKey('Note')
    order = models.PositiveIntegerField()
    string = models.TextField(blank=True)
    start_stop_list = models.TextField(default="[]")

class Address(DateObject, SecondaryObject):
    locations = models.ManyToManyField('Location', null=True)

class Location(models.Model):
    street = models.TextField(blank=True)
    city = models.TextField(blank=True)
    county = models.TextField(blank=True)
    state = models.TextField(blank=True)
    country = models.TextField(blank=True)
    postal = models.TextField(blank=True)
    phone = models.TextField(blank=True)
    parish = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()

## FIXME:
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

    order = models.PositiveIntegerField()
    last_changed = models.DateTimeField('last changed', auto_now=True)
    private = models.BooleanField()
  
class NoteRef(BaseRef):
    ref_object = models.ForeignKey('Note') 

    def __unicode__(self):
        return "NoteRef to " + str(self.ref_object)

class SourceRef(DateObject, BaseRef):
    ref_object = models.ForeignKey('Source')
    page = models.CharField(max_length=50)
    confidence = models.IntegerField()

    def __unicode__(self):
        return "SourceRef to " + str(self.ref_object)

class EventRef(BaseRef):
    ref_object = models.ForeignKey('Event')
    role_type = models.ForeignKey('EventRoleType')

    def __unicode__(self):
        return "EventRef to " + str(self.ref_object)

class RepositoryRef(BaseRef):
    ref_object = models.ForeignKey('Repository')
    source_media_type = models.ForeignKey('SourceMediaType')
    call_number = models.CharField(max_length=50)

    def __unicode__(self):
        return "RepositoryRef to " + str(self.ref_object)

class PersonRef(BaseRef):
    ref_object = models.ForeignKey('Person')
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return "PersonRef to " + str(self.ref_object)

class ChildRef(BaseRef):
    father_rel_type = models.ForeignKey('FamilyRelType', related_name="father_rel")
    mother_rel_type = models.ForeignKey('FamilyRelType', related_name="mother_rel")
    ref_object = models.ForeignKey('Person')

    def __unicode__(self):
        return "ChildRef to " + str(self.ref_object)

class MediaRef(BaseRef):
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    ref_object = models.ForeignKey('Media')

    def __unicode__(self):
        return "MediaRef to " + str(self.ref_object)

#--------------------------------------------------------------------------------
#
# Testing Functions
#
#--------------------------------------------------------------------------------

## Primary:

def test_Person():
    (val, name) = MarkerType.get_default()
    m = MarkerType.objects.get(val=val, name=name)
    p = Person(handle=create_id(), marker_type=m)
    p.gender_type = GenderType.objects.get(id=1) 
    p.gramps_id = "P%05d" % (Person.objects.count() + 1)
    p.save()
    return p

def test_Family():
    m = MarkerType.objects.get(id=1)
    frt = FamilyRelType.objects.get(id=1)
    f = Family(handle=create_id(), marker_type=m, family_rel_type=frt)
    f.gramps_id = "F%05d" % (Family.objects.count() + 1)
    f.save()
    return f

def test_Source():
    m = MarkerType.objects.get(id=1)
    s = Source(handle=create_id(), marker_type=m)
    s.save()
    s.gramps_id = "S%05d" % (Source.objects.count() + 1)
    s.save()
    return s

def test_Event():
    m = MarkerType.objects.get(id=1)
    et = EventType.objects.get(id=1)
    e = Event(handle=create_id(), marker_type=m, event_type=et)
    e.set_date_from_gdate( GDate() )
    e.gramps_id = "E%05d" % (Event.objects.count() + 1)
    e.save()
    return e

def test_Repository():
    m = MarkerType.objects.get(id=1)
    rt = RepositoryType.objects.get(id=1)
    r = Repository(handle=create_id(), marker_type=m, repository_type=rt)
    r.gramps_id = "R%05d" % (Repository.objects.count() + 1)
    r.save()
    return r

def test_Place():
    m = MarkerType.objects.get(id=1)
    p = Place(handle=create_id(), marker_type=m)
    p.gramps_id = "L%05d" % (Place.objects.count() + 1)
    p.save()
    return p
    
def test_Media():
    m = MarkerType.objects.get(id=1)
    media = Media(handle=create_id(), marker_type=m)
    media.save()
    media.gramps_id = "M%05d" % (Media.objects.count() + 1)
    return media

def test_Note():
    m = MarkerType.objects.get(id=1)
    note_type = NoteType.objects.get(id=1)
    note = Note(handle=create_id(), marker_type=m, note_type=note_type, 
                preformatted=False)
    note.gramps_id = "N%05d" % (Note.objects.count() + 1)
    note.save()
    return note

def test_Family_with_children():
    father = test_Person()
    fname = test_Name(father, "Blank", "Lowell")
    mother = test_Person()
    mname = test_Name(mother, "Bamford", "Norma")
    family_rel_type = FamilyRelType.objects.get(id=1)
    m = MarkerType.objects.get(id=1)
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
    m = MarkerType.objects.get(id=1)
    n = Name()
    if first:
        n.first_name = first
    if surname:
        n.surname = surname
    n.set_date_from_gdate(Today())
    n.name_type = NameType.objects.get(id=1)
    n.order = 1
    n.sort_as = 1
    n.display_as = 1
    n.save()
    person.names.add(n)
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
    note_ref = NoteRef(referenced_by=person, ref_object=note)
    note_ref.order = 1
    note_ref.save()
    family = test_Family()
    note_ref = NoteRef(referenced_by=family, ref_object=note)
    note_ref.order = 1
    note_ref.save()
    return note_ref

def test_SourceRef():
    note = test_Note()
    source = test_Source()
    source_ref = SourceRef(referenced_by=note, ref_object=source, confidence=4)
    source_ref.set_date_from_gdate(Today())
    source_ref.order = 1
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

    sourceref = test_SourceRef()
    print sourceref.source.references.all()

if __name__ == "__main__":
    main()
