from grampsweb.grampsdb.models import *
from django.contrib import admin


for obj in (MarkerType, NameType, AttributeType, UrlType, ChildRefType, 
            RepositoryType, EventType, FamilyRelType, SourceMediaType, 
            EventRoleType, NoteType, 
            Name, Address, Event, Note, Source, Place, Media, 
            Repository, NoteRef, SourceRef, EventRef, 
            RepositoryRef, PersonRef, ChildRef, MediaRef, Person, 
            Family, Lds, Markup):
    admin.site.register(obj)
