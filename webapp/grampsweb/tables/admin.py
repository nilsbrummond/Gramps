from grampsweb.tables.models import *
from django.contrib import admin

for obj in (MarkerType, NameType, AttributeType, UrlType, ChildRefType, 
            RepositoryType, EventType, FamilyRelType, SourceMediaType, 
            EventRoleType, NoteType, TagType, Handle, Event, Note, EventRef, 
            Person, Name):
    admin.site.register(obj)


