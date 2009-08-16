"""
Clears gramps data
"""

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
import settings

import grampsdb.models as dj

dj.Address.objects.all().delete()
    #dj.AttributeType.objects.all().delete()
dj.ChildRef.objects.all().delete()
    #dj.ChildRefType.objects.all().delete()
dj.Event.objects.all().delete()
dj.EventRef.objects.all().delete()
    #dj.EventRoleType.objects.all().delete()
    #dj.EventType.objects.all().delete()
dj.Family.objects.all().delete()
    #dj.FamilyRelType.objects.all().delete()
    #dj.GenderType.objects.all().delete()
dj.Lds.objects.all().delete()
dj.Location.objects.all().delete()
    #dj.MarkerType.objects.all().delete()
dj.Markup.objects.all().delete()
dj.Media.objects.all().delete()
dj.MediaRef.objects.all().delete()
dj.Name.objects.all().delete()
    #dj.NameType.objects.all().delete()
dj.Note.objects.all().delete()
dj.NoteRef.objects.all().delete()
    #dj.NoteType.objects.all().delete()
dj.Person.objects.all().delete()
dj.PersonRef.objects.all().delete()
dj.Place.objects.all().delete()
dj.Repository.objects.all().delete()
dj.RepositoryRef.objects.all().delete()
    #dj.RepositoryType.objects.all().delete()
dj.Source.objects.all().delete()
    #dj.SourcemediaType.objects.all().delete()
dj.SourceRef.objects.all().delete()
    #dj.UrlType.objects.all().delete()
