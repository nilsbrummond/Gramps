# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008 - 2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2009         B. Malengier <benny.malengier@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$
#

"""
Import from the Django Models on the configured database backend

"""

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
from gettext import ngettext
import time
import sys
import os
import pdb

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ImportDjango")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.lib
from QuestionDialog import ErrorDialog
from gen.plug import PluginManager, ImportPlugin
from Utils import create_id
import const

#django initialization
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    loc = os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
#make sure django can find the webapp modules
sys.path += [const.ROOT_DIR + os.sep + '..' + os.sep + 'webapp' ]
sys.path += [const.ROOT_DIR + os.sep + '..' + os.sep + 'webapp' + os.sep + 'grampsweb' ]

import grampsweb.grampsdb.models as dj
from django.contrib.contenttypes.models import ContentType

#-------------------------------------------------------------------------
#
# Import functions
#
#-------------------------------------------------------------------------
def lookup_role_index(role0, event_ref_list):
    """
    Find the handle in a unserialized event_ref_list and return code.
    """
    if role0 is None:
        return -1
    else:
        count = 0
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, erole) = event_ref
            event = dj.Event.objects.get(handle=ref)
            if event.event_type[0] == role0:
                return count
            count += 1
        return -1

def totime(dtime):
    return int(time.mktime(dtime.timetuple()))

#-------------------------------------------------------------------------
#
# Django Reader
#
#-------------------------------------------------------------------------
class DjangoReader(object):
    def __init__(self, db, filename, callback):
        if not callable(callback): 
            callback = lambda (percent): None # dummy
        self.db = db
        self.filename = filename
        self.callback = callback
        self.debug = 0

    # -----------------------------------------------
    # Get methods to retrieve list data from the tables
    # -----------------------------------------------

    def get_names(self, person, preferred):
        names = person.name_set.filter(preferred=preferred).order_by("order")
        if preferred:
            if len(names) > 0:
                return self.pack_name(names[0])
            else:
                return gen.lib.Name().serialize()
        else:
            return [self.pack_name(name) for name in names]
     
    def get_datamap(self, obj): # obj is source
        datamap_dict = {}
        datamap_list = obj.datamap_set.all()
        for datamap in datamap_list:
            datamap_dict[datamap.key] = datamap.value
        return datamap_dict

    def pack_url(url):
        return  (url.private, url.path, url.desc, tuple(url_type))

    def get_attribute_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        attribute_list = dj.Attribute.objects.filter(object_id=obj.id, 
                                                     object_type=obj_type)
        return [self.pack_attribute(attribute) for attribute 
                in attribute_list]

    def pack_attribute(self, attribute):
        source_list = self.get_source_ref_list(attribute)
        note_list = self.get_note_list(attribute)
        return (attribute.private, 
                source_list, 
                note_list, 
                tuple(attribute.attribute_type), 
                attribute.value)

    def get_media_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        mediarefs = dj.MediaRef.objects.filter(object_id=obj.id, 
                                               object_type=obj_type)
        retval = []
        for mediaref in mediarefs:
            retval.append(self.pack_media_ref(mediaref))
        return retval

    def get_note_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        noterefs = dj.NoteRef.objects.filter(object_id=obj.id, 
                                             object_type=obj_type)
        retval = []
        for noteref in noterefs:
            retval.append( noteref.ref_object.handle)
        return retval

    def get_repository_ref_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        reporefs = dj.RepositoryRef.objects.filter(object_id=obj.id, 
                                                   object_type=obj_type)
        return [self.pack_repository_ref(repo) for repo in reporefs]

    def get_url_list(self, obj):
        return [self.pack_url(url) for url in obj.url_set.all().order_by("order")]

    def get_address_list(self, obj, with_parish): # person or repository
        addresses = obj.address_set.all().order_by("order")
        retval = []
        count = 1
        for address in addresses:
            retval.append(self.pack_address(address, with_parish))
            count += 1
        return retval

    def get_child_ref_list(self, family):
        obj_type = ContentType.objects.get_for_model(family)
        childrefs = dj.ChildRef.objects.filter(object_id=family.id, \
                                                   object_type=obj_type).order_by("order")
        retval = []
        for childref in childrefs:
            retval.append(self.pack_child_ref(childref))
        return retval

    def get_source_ref_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        sourcerefs = dj.SourceRef.objects.filter(object_id=obj.id, \
                                  object_type=obj_type).order_by("order")
        retval = []
        for sourceref in sourcerefs:
            retval.append(self.pack_source_ref(sourceref))
        return retval

    def get_event_ref_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        eventrefs = dj.EventRef.objects.filter(object_id=obj.id, \
                                  object_type=obj_type).order_by("order")
        retval = []
        for eventref in eventrefs:
            retval.append(self.pack_event_ref(eventref))
        return retval

    def get_family_list(self, person): # person has families
        return [fam.handle for fam in person.families.all()]

    def get_parent_family_list(self, person):
        return [fam.handle for fam in person.parent_families.all()]

    def get_person_ref_list(self, person):
        obj_type = ContentType.objects.get_for_model(person)
        return [self.pack_person_ref(x) for x in 
                dj.PersonRef.objects.filter(object_id=person.id, 
                                            object_type=obj_type)]

    def get_lds_list(self, obj): # person or family
        return [self.pack_lds(lds) for lds in obj.lds_set.all().order_by("order")]

    def get_place_handle(self, obj): # obj is event
        if obj.place:
            return obj.place.handle
        return ''

    ## Packers:

    def get_event(self, event):
        handle = event.handle
        gid = event.gramps_id
        the_type = tuple(event.event_type)
        description = event.description
        change = totime(event.last_changed)
        marker = tuple(event.marker_type)
        private = event.private
        note_list = self.get_note_list(event)           
        source_list = self.get_source_ref_list(event)   
        media_list = self.get_media_list(event)         
        attribute_list = self.get_attribute_list(event)
        date = self.get_date(event)
        place = self.get_place_handle(event)
        return (str(handle), gid, the_type, date, description, place, 
                source_list, note_list, media_list, attribute_list,
                change, marker, private)

    def get_note(self, note):
        styled_text = [note.text, []]
        markups = dj.Markup.objects.filter(note=note).order_by("order")
        for markup in markups:
            value = markup.string
            start_stop_list  = markup.start_stop_list
            ss_list = eval(start_stop_list)
            styled_text[1] += [(tuple(markup.markup_type), 
                                value, ss_list)]
        changed = totime(note.last_changed)
        return (str(note.handle), 
                note.gramps_id, 
                styled_text, 
                note.preformatted, 
                tuple(note.note_type), 
                changed, 
                tuple(note.marker_type), 
                note.private)

    def get_family(self, family):
        child_ref_list = self.get_child_ref_list(family)
        event_ref_list = self.get_event_ref_list(family)
        media_list = self.get_media_list(family)
        attribute_list = self.get_attribute_list(family)
        lds_seal_list = self.get_lds_list(family)
        source_list = self.get_source_ref_list(family)
        note_list = self.get_note_list(family)
        if family.father:
            father_handle = family.father.handle
        else:
            father_handle = ''
        if family.mother:
            mother_handle = family.mother.handle
        else:
            mother_handle = ''
        return (str(family.handle), family.gramps_id, 
                father_handle, mother_handle,
                child_ref_list, tuple(family.family_rel_type), 
                event_ref_list, media_list,
                attribute_list, lds_seal_list, 
                source_list, note_list,
                totime(family.last_changed), 
                tuple(family.marker_type), 
                family.private)

    def get_repository(self, repository):
        note_list = self.get_note_list(repository)
        address_list = self.get_address_list(repository, with_parish=False)
        url_list = self.get_url_list(repository)
        return (str(repository.handle), 
                repository.gramps_id, 
                tuple(repository.repository_type),
                repository.name, 
                note_list,
                address_list, 
                url_list, 
                totime(repository.last_changed), 
                tuple(repository.marker_type), 
                repository.private)

    def pack_place(self, place):
        locations = place.location_set.all().order_by("order")
        main_loc = None
        alt_location_list = []
        for location in locations:
            if main_loc is None:
                main_loc = self.pack_location(location, True)
            else:
                alt_location_list.append(self.pack_location(location, True))
        url_list = self.get_url_list(place)
        media_list = self.get_media_list(place)
        source_list = self.get_source_ref_list(place)
        note_list = self.get_note_list(place)
        return (str(place.handle), 
                place.gramps_id,
                place.title, 
                place.long, 
                place.lat,
                main_loc, 
                alt_location_list,
                url_list,
                media_list,
                source_list,
                note_list,
                totime(place.last_changed), 
                tuple(place.marker_type), 
                place.private)

    def get_source(self, source):
        note_list = self.get_note_list(source)
        media_list = self.get_media_list(source)
        datamap = self.get_datamap(source)
        reporef_list = self.get_repository_ref_list(source)
        return (str(source.handle), 
                source.gramps_id, 
                source.title,
                source.author, 
                source.pubinfo,
                note_list,
                media_list,
                source.abbrev,
                totime(source.last_changed), 
                datamap,
                reporef_list,
                tuple(source.marker_type), 
                source.private)

    def get_media(self, media):
        attribute_list = self.get_attribute_list(media)
        source_list = self.get_source_ref_list(media)
        note_list = self.get_note_list(media)
        date = self.get_date(media)
        return (str(media.handle), 
                media.gramps_id, 
                media.path, 
                media.mime, 
                media.desc,
                attribute_list,
                source_list,
                note_list,
                totime(media.last_changed),
                date,
                tuple(media.marker_type),
                media.private)

    def get_person(self, person):
        primary_name = self.get_names(person, True) # one
        alternate_names = self.get_names(person, False) # list
        event_ref_list = self.get_event_ref_list(person)
        family_list = self.get_family_list(person)
        parent_family_list = self.get_parent_family_list(person)
        media_list = self.get_media_list(person)
        address_list = self.get_address_list(person, with_parish=False)
        attribute_list = self.get_attribute_list(person)
        url_list = self.get_url_list(person)
        lds_ord_list = self.get_lds_list(person)
        psource_list = self.get_source_ref_list(person)
        pnote_list = self.get_note_list(person)
        person_ref_list = self.get_person_ref_list(person)
        # This looks up the events for the first EventType given:
        death_ref_index = lookup_role_index(dj.EventType.DEATH, event_ref_list)
        birth_ref_index = lookup_role_index(dj.EventType.BIRTH, event_ref_list)
        return (str(person.handle),
                person.gramps_id,  
                tuple(person.gender_type)[0],
                primary_name,       
                alternate_names,    
                death_ref_index,    
                birth_ref_index,    
                event_ref_list,     
                family_list,        
                parent_family_list, 
                media_list,         
                address_list,       
                attribute_list,     
                url_list,               
                lds_ord_list,       
                psource_list,       
                pnote_list,         
                totime(person.last_changed),             
                tuple(person.marker_type), 
                person.private,            
                person_ref_list)

    # ---------------------------------
    # Packers
    # ---------------------------------

    ## The packers build GRAMPS raw unserialized data.

    ## Reference packers

    def pack_child_ref(self, child_ref):
        source_list = self.get_source_ref_list(child_ref)
        note_list = self.get_note_list(child_ref) 
        return (child_ref.private, source_list, note_list, child_ref.ref_object.handle, 
                tuple(child_ref.father_rel_type), tuple(child_ref.mother_rel_type))

    def pack_person_ref(self, personref):
        source_list = self.get_source_ref_list(personref)
        note_list = self.get_note_list(personref)
        return (personref.private, 
                source_list,
                note_list,
                personref.ref_object.handle,
                personref.description)

    def pack_media_ref(self, media_ref):
        source_list = self.get_source_ref_list(media_ref)
        note_list = self.get_note_list(media_ref)
        attribute_list = self.get_attribute_list(media_ref)
        if ((media_ref.x1 == media_ref.y1 == media_ref.x2 == media_ref.y2 == -1) or
            (media_ref.x1 == media_ref.y1 == media_ref.x2 == media_ref.y2 == 0)):
            role = None
        else:
            role = (media_ref.x1, media_ref.y1, media_ref.x2, media_ref.y2)
        return (media_ref.private, source_list, note_list, attribute_list, 
                media_ref.ref_object.handle, role)

    def pack_repository_ref(self, repo_ref):
        note_list = self.get_note_list(repo_ref)
        return (note_list, 
                repo_ref.ref_object.handle,
                repo_ref.call_number, 
                tuple(repo_ref.source_media_type),
                repo_ref.private)

    def pack_media_ref(self, media_ref):
        note_list = self.get_note_list(media_ref)
        attribute_list = self.get_attribute_list(media_ref)
        source_list = self.get_source_ref_list(media_ref)
        return (media_ref.private, source_list, note_list, attribute_list, 
                media_ref.ref_object.handle, (media_ref.x1,
                                              media_ref.y1,
                                              media_ref.x2,
                                              media_ref.y2))
    
    def pack_event_ref(self, event_ref):
        note_list = self.get_note_list(event_ref)
        attribute_list = self.get_attribute_list(event_ref)
        return (event_ref.private, note_list, attribute_list, 
                event_ref.ref_object.handle, tuple(event_ref.role_type))

    def pack_source_ref(self, source_ref):
        ref = source_ref.ref_object.handle
        confidence = source_ref.confidence
        page = source_ref.page
        private = source_ref.private
        date = self.get_date(source_ref)
        note_list = self.get_note_list(source_ref)
        return (date, private, note_list, confidence, ref, page)

    def pack_address(self, address, with_parish):
        source_list = self.get_source_ref_list(address)
        date = self.get_date(address)
        note_list = self.get_note_list(address)
        locations = address.location_set.all().order_by("order")
        if len(locations) > 0:
            location = self.pack_location(locations[0], with_parish)
        else:
            if with_parish:
                location = (("", "", "", "", "", "", ""), "")
            else:
                location = ("", "", "", "", "", "", "")
        return (address.private, source_list, note_list, date, location)

    def pack_lds(self, lds):
        source_list = self.get_source_ref_list(lds)
        note_list = self.get_note_list(lds)
        date = self.get_date(lds)
        if lds.famc:
            famc = lds.famc.handle
        else:
            famc = None
        place = self.get_place_handle(lds)
        return (source_list, note_list, date, lds.lds_type[0], place,
                famc, lds.temple, lds.status[0], lds.private)

    def pack_url(self, url):
        return  (url.private, url.path, url.desc, tuple(url.url_type))

    def pack_source(self, source):
        note_list = self.get_note_list(source)
        media_list = self.get_media_list(source)
        reporef_list = self.get_repository_ref_list(source)
        datamap = self.get_datamap(source)
        return (source.handle, source.gramps_id, source.title,
                source.author, source.pubinfo,
                note_list,
                media_list,
                source.abbrev,
                totime(last_changed), datamap,
                reporef_list,
                tuple(source.marker_type), source.private)

    def pack_name(self, name):
        source_list = self.get_source_ref_list(name)
        note_list = self.get_note_list(name)
        date = self.get_date(name)
        return (name.private, source_list, note_list, date,
                name.first_name, name.surname, name.suffix, name.title,
                tuple(name.name_type), name.prefix, name.patronymic,
                name.group_as, name.sort_as, name.display_as, name.call)

    def pack_location(self, loc, with_parish):
        if with_parish:
            return ((loc.street, loc.city, loc.county, loc.state, loc.country, 
                     loc.postal, loc.phone), loc.parish)
        else:
            return (loc.street, loc.city, loc.county, loc.state, loc.country, 
                    loc.postal, loc.phone)

    def get_date(self, obj):
        if ((obj.calendar == obj.modifier == obj.quality == obj.sortval == obj.newyear == 0) and
            obj.text == "" and (not obj.slash1) and (not obj.slash2) and 
            (obj.day1 == obj.month1 == obj.year1 == 0) and 
            (obj.day2 == obj.month2 == obj.year2 == 0)):
            return None
        elif ((not obj.slash1) and (not obj.slash2) and 
            (obj.day2 == obj.month2 == obj.year2 == 0)):
            dateval = (obj.day1, obj.month1, obj.year1, obj.slash1)
        else:
            dateval = (obj.day1, obj.month1, obj.year1, obj.slash1, 
                       obj.day2, obj.month2, obj.year2, obj.slash2)
        return (obj.calendar, obj.modifier, obj.quality, dateval, 
                obj.text, obj.sortval, obj.newyear)

    def process(self):
        sql = None
        total = (dj.Note.objects.count() + 
                 dj.Person.objects.count() + 
                 dj.Event.objects.count() +
                 dj.Family.objects.count() +
                 dj.Repository.objects.count() +
                 dj.Place.objects.count() +
                 dj.Media.objects.count() +
                 dj.Source.objects.count())
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        count = 0.0
        self.t = time.time()

        # ---------------------------------
        # Process note
        # ---------------------------------
        notes = dj.Note.objects.all()
        for note in notes:
            data = self.get_note(note)
            self.db.note_map[str(note.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process event
        # ---------------------------------
        events = dj.Event.objects.all()
        for event in events:
            data = self.get_event(event)
            self.db.event_map[str(event.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process person
        # ---------------------------------
        ## Do this after Events to get the birth/death data
        people = dj.Person.objects.all()
        for person in people:
            data = self.get_person(person)
            self.db.person_map[str(person.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process family
        # ---------------------------------
        families = dj.Family.objects.all()
        for family in families:
            data = self.get_family(family)
            self.db.family_map[str(family.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process repository
        # ---------------------------------
        repositories = dj.Repository.objects.all()
        for repo in repositories:
            data = self.get_repository(repo)
            self.db.repository_map[str(repo.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process place
        # ---------------------------------
        places = dj.Place.objects.all()
        for place in places:
            data = self.pack_place(place)
            self.db.place_map[str(place.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process source
        # ---------------------------------
        sources = dj.Source.objects.all()
        for source in sources:
            data = self.get_source(source)
            self.db.source_map[str(source.handle)] = data
            count += 1
            self.callback(100 * count/total)

        # ---------------------------------
        # Process media
        # ---------------------------------
        media = dj.Media.objects.all()
        for med in media:
            data = self.get_media(med)
            self.db.media_map[str(med.handle)] = data
            count += 1
            self.callback(100 * count/total)


        return None

    def cleanup(self):
        self.t = time.time() - self.t
        msg = ngettext('Import Complete: %d second','Import Complete: %d seconds', self.t ) % self.t
        self.db.transaction_commit(self.trans,_("Django import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        print msg


def import_data(db, filename, callback=None):
    g = DjangoReader(db, filename, callback)
    g.process()
    g.cleanup()

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
_name = _('Django Import')
_description = _('Django can read SQLite, MySQL, PostgreSQL, Oracle, and others.')

pmgr = PluginManager.get_instance()
plugin = ImportPlugin(name            = _('Django Database'), 
                      description     = _("Import data from Django database"),
                      import_function = import_data,
                      extension       = "django")
pmgr.register_plugin(plugin)

