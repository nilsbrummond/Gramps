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
# $Id: ExportSql.py 12940 2009-08-10 01:25:34Z dsblank $
#

"""
Export to the Django Models on the configured database backend


"""

#------------------------------------------------------------------------
#
# Standard Python Modules
#
#------------------------------------------------------------------------
import sys
import os
from gettext import gettext as _
from gettext import ngettext
import time

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ExportDjango")

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from gen.plug import PluginManager, ExportPlugin
import ExportOptions
from Utils import create_id
import const
import gen.lib

#django initialization
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    loc = os.environ["DJANGO_SETTINGS_MODULE"] = 'settings'
#make sure django can find the webapp modules
sys.path += [const.ROOT_DIR + os.sep + '..' + os.sep + 'webapp' ]
sys.path += [const.ROOT_DIR + os.sep + '..' + os.sep + 'webapp' + os.sep + 'grampsweb' ]

import grampsweb.grampsdb.models as dj

CUSTOMMARKER = {}
#-------------------------------------------------------------------------
#
# Export functions
#
#-------------------------------------------------------------------------
def todate(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

def lookup(index, event_ref_list):
    """
    Get the unserialized event_ref in an list of them and return it.
    """
    if index < 0:
        return None
    else:
        count = 0
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            if index == count:
                return ref
            count += 1
        return None

def get_datamap(grampsclass):
    return [x[0] for x in grampsclass._DATAMAP if x[0] != grampsclass.CUSTOM]

def make_db():
    """
    Prepares the database.
    """
    dj.clear_tables("primary", "secondary")

## Export lists:

def export_child_ref_list(obj, ref_list):
    ## Currently, only Family references children
    for child_data in ref_list:
        export_child_ref(obj, child_data)

def export_source_ref_list(obj, source_list):
    for source_data in source_list:
        export_source_ref(obj, source_data)

def export_event_ref_list(obj, event_ref_list):
    for event_ref in event_ref_list:
        export_event_ref(obj, event_ref)

def export_note_list(obj, note_list):
    for handle in note_list:
        # Just the handle
        note = dj.Note.objects.get(handle=handle)
        export_note_ref(obj, note)

def export_alternate_name_list(person, alternate_names):
    for name in alternate_names:
        if name:
            export_name(person, name, False)

def export_parent_family_list(person, parent_family_list):
    for parent_family_data in parent_family_list:
        export_parent_family(person, parent_family_data)

def export_media_ref_list(person, media_list):
    for media_data in media_list:
        export_media_ref(person, media_data)

def export_attribute_list(obj, attribute_list):
    for attribute_data in attribute_list:
        export_attribute(obj, attribute_data)

def export_url_list(obj, url_list):
    if not url_list: return None
    count = 1
    for url_data in url_list:
        export_url(obj, url_data, count) 
        count += 1
        
def export_person_ref_list(obj, person_ref_list):
    for person_ref_data in person_ref_list:
        export_person_ref(obj, person_ref_data)

def export_address_list(obj, address_list):
    count = 1
    for address_data in address_list:
        export_address(obj, address_data, count)
        count += 1

def export_lds_list(person, lds_ord_list):
    count = 1
    for ldsord in lds_ord_list:
        export_lds(person, ldsord, count)
        count += 1

def export_repository_ref_list(obj, reporef_list):
    for data in reporef_list:
        export_repository_ref(obj, data)

def export_family_ref_list(person, family_list):
    for family_handle in family_list:
        export_family_ref(person, family_handle) 

## Export reference objects:

def export_person_ref(obj, person_ref_data):
    (private, 
     source_list,
     note_list,
     handle,
     desc) = person_ref_data
    person = dj.Person.objects.get(handle=handle)
    count = person.references.count()
    person_ref = dj.PersonRef(referenced_by=obj,
                              ref_object=person,
                              private=private,
                              order=count + 1,
                              description=desc)
    person_ref.save()
    export_note_list(person_ref, note_list)
    export_source_ref_list(person_ref, source_list)

def export_note_ref(obj, note):
    count = note.references.count()
    note_ref = dj.NoteRef(referenced_by=obj, 
                          ref_object=note,
                          private=False,
                          order=count + 1)
    note_ref.save()

def export_media_ref(obj, media_ref_data):
    (private, source_list, note_list, attribute_list, 
     ref, role) = media_ref_data
    media = dj.Media.objects.get(handle=ref)
    count = media.references.count()
    if not role:
        role = (0,0,0,0)
    media_ref = dj.MediaRef(referenced_by=obj, 
                            ref_object=media,
                            x1=role[0],
                            y1=role[1],
                            x2=role[2],
                            y2=role[3],
                            private=private,
                            order=count + 1)
    media_ref.save()
    export_note_list(media_ref, note_list)
    export_attribute_list(media_ref, attribute_list)
    export_source_ref_list(media_ref, source_list)

def export_source_ref(obj, source_data):
    (date, private, note_list, confidence, ref, page) = source_data
    source = dj.Source.objects.get(handle=ref)
    count = source.references.count()
    source_ref = dj.SourceRef(private=private, 
                              confidence=confidence, 
                              page=page, 
                              order=count + 1,
                              referenced_by=obj, 
                              ref_object=source)
    export_date(source_ref, date)
    source_ref.save()
    export_note_list(source_ref, note_list) 
    
def export_child_ref(obj, data):
    (private, source_list, note_list, ref, frel, mrel) = data
    child = dj.Person.objects.get(handle=ref)
    count = dj.ChildRef.objects.filter(object_id=obj.id,object_type=obj).count()
    child_ref = dj.ChildRef(private=private,
                            referenced_by=obj,
                            ref_object=child,
                            order=count + 1,
                            father_rel_type=dj.get_type(dj.ChildRefType, frel),
                            mother_rel_type=dj.get_type(dj.ChildRefType, mrel))
    child_ref.save()
    export_source_ref_list(child_ref, source_list)
    export_note_list(child_ref, note_list)

def export_event_ref(obj, event_data):
    (private, note_list, attribute_list, ref, role) = event_data
    event = dj.Event.objects.get(handle=ref)
    count = dj.EventRef.objects.filter(object_id=obj.id,object_type=obj).count()
    event_ref = dj.EventRef(private=private,
                            referenced_by=obj,
                            ref_object=event,
                            order=count + 1,
                            role_type = dj.get_type(dj.EventRoleType, role))
    event_ref.save()
    export_note_list(event_ref, note_list)
    export_attribute_list(event_ref, attribute_list)

def export_repository_ref(obj, reporef_data):
    (note_list, 
     ref,
     call_number, 
     source_media_type,
     private) = reporef_data
    repository = dj.Repository.objects.get(handle=ref)
    count = dj.RepositoryRef.objects.filter(object_id=obj.id,object_type=obj).count()
    repos_ref = dj.RepositoryRef(private=private,
                                 referenced_by=obj,
                                 call_number=call_number,
                                 source_media_type=dj.get_type(dj.SourceMediaType,
                                                            source_media_type),
                                 ref_object=repository,
                                 order=count + 1)
    repos_ref.save()
    export_note_list(repos_ref, note_list)

def export_family_ref(obj, handle):
    family = dj.Family.objects.get(handle=handle)
    obj.families.add(family)
    obj.save()

## Export individual objects:

def export_datamap_dict(source, datamap_dict):
    for key in datamap_dict:
        value = datamap_dict[key]
        datamap = dj.Datamap(key=key, value=value)
        datamap.save()
        source.datamaps.add(datamap)
        source.save()

def export_lds(person, data, order):
    (lsource_list, lnote_list, date, type, place_handle,
     famc_handle, temple, status, private) = data
    if place_handle:
        place = dj.Place.objects.get(handle=place_handle)
    else:
        place = None
    if famc_handle:
        famc = dj.Family.objects.get(handle=famc_handle)
    else:
        famc = None
    lds = dj.Lds(lds_type = dj.get_type(dj.LdsType, type),
                 temple=temple, 
                 place=place,
                 famc=famc,
                 order=order,
                 status = dj.get_type(dj.LdsStatus, status),
                 private=private)
    export_date(lds, date)
    lds.save()
    export_note_list(lds, lnote_list)
    export_source_ref_list(lds, lsource_list)

def export_address(obj, address_data, order):
    (private, asource_list, anote_list, date, location) = address_data
    address = dj.Address(private=private, order=order)
    export_date(address, date)
    address.save()
    export_location(address, location, 1)
    export_note_list(address, anote_list) 
    export_source_ref_list(address, asource_list)
    address.save()
    obj.save()
    obj.addresses.add(address)
    obj.save()

def export_attribute(obj, attribute_data):
    (private, source_list, note_list, the_type, value) = attribute_data
    attribute_type = dj.get_type(dj.AttributeType, the_type)
    attribute = dj.Attribute(private=private,
                             attribute_type=attribute_type,
                             value=value)
    attribute.save()
    export_source_ref_list(attribute, source_list)
    export_note_list(attribute, note_list)
    obj.attributes.add(attribute)
    obj.save()

def export_url(obj, url_data, order):
    (private, path, desc, type) = url_data
    url = dj.Url(private=private,
                 path=path,
                 desc=desc,
                 order=order,
                 url_type=dj.get_type(dj.UrlType, type))
    url.save()
    obj.url_list.add(url)
    obj.save()

def export_place_ref(event, place_handle):
    if place_handle:
        place = dj.Place.objects.get(handle=place_handle)
        event.place = place
        event.save()

def export_parent_family(person, parent_family_handle):
    # handle
    family = dj.Family.objects.get(handle=parent_family_handle)
    person.parent_families.add(family)
    person.save()

def export_date(obj, date):
    if date is None: 
        (calendar, modifier, quality, text, sortval, newyear) = \
            (0, 0, 0, "", 0, 0)
        day1, month1, year1, slash1 = 0, 0, 0, 0
        day2, month2, year2, slash2 = 0, 0, 0, 0
    else:
        (calendar, modifier, quality, dateval, text, sortval, newyear) = date
        if len(dateval) == 4:
            day1, month1, year1, slash1 = dateval
            day2, month2, year2, slash2 = 0, 0, 0, 0
        elif len(dateval) == 8:
            day1, month1, year1, slash1, day2, month2, year2, slash2 = dateval
        else:
            raise ("ERROR: date dateval format", dateval)
    obj.calendar = calendar
    obj.modifier = modifier
    obj.quality = quality
    obj.text = text
    obj.sortval = sortval
    obj.newyear = newyear
    obj.day1 = day1
    obj.month1 = month1
    obj.year1 = year1
    obj.slash1 = slash1
    obj.day2 = day2
    obj.month2 = month2
    obj.year2 = year2
    obj.slash2 = slash2

def export_name(person, data, preferred):
    # A Step #2 function
    if data:
        (private, source_list, note_list, date,
         first_name, surname, suffix, title,
         name_type, prefix, patronymic,
         group_as, sort_as, display_as, call) = data

        count = person.names.count()
        name = dj.Name()
        name.order = count + 1
        name.preferred = preferred
        name.private = private
        name.first_name = first_name
        name.surname = surname
        name.suffix = suffix
        name.title = title
        name.name_type = dj.get_type(dj.NameType, name_type)
        name.prefix = prefix
        name.patronymic = patronymic
        name.group_as = group_as
        name.sort_as = sort_as
        name.display_as = display_as 
        name.call = call
        export_date(name, date) 
        name.save()
        person.names.add(name)
        person.save()
        export_note_list(person, note_list)
        export_source_ref_list(person, source_list)
        person.save()
       
## Export primary objects:

def export_person(data, step):
    # Unpack from the BSDDB:
    (handle,        #  0
     gid,          #  1
     gender,             #  2
     primary_name,       #  3
     alternate_names,    #  4
     death_ref_index,    #  5
     birth_ref_index,    #  6
     event_ref_list,     #  7
     family_list,        #  8
     parent_family_list, #  9
     media_list,         # 10
     address_list,       # 11
     attribute_list,     # 12
     url_list,               # 13
     lds_ord_list,       # 14
     psource_list,       # 15
     pnote_list,         # 16
     change,             # 17
     marker,             # 18
     private,           # 19
     person_ref_list,    # 20
     ) = data

    if step == 0:     # Add the primary data:
        person = dj.Person(handle=handle,
                           gramps_id=gid,
                           last_changed=todate(change),
                           private=private,
                           marker_type = dj.get_type(dj.MarkerType, marker),
                           gender_type = dj.get_type(dj.GenderType, gender))
        person.save()

    elif step == 1:   # Add the relations:
        person = dj.Person.objects.get(handle=handle)
        if primary_name:
            export_name(person, primary_name, True)
        export_alternate_name_list(person, alternate_names)
        export_event_ref_list(person, event_ref_list)
        export_family_ref_list(person, family_list) 
        export_parent_family_list(person, parent_family_list)
        export_media_ref_list(person, media_list)
        export_note_list(person, pnote_list)
        export_attribute_list(person, attribute_list)
        export_url_list(person, url_list) 
        export_person_ref_list(person, person_ref_list)
        export_source_ref_list(person, psource_list)
        export_address_list(person, address_list)
        export_lds_list(person, lds_ord_list)

def export_note(data, step):
    # Unpack from the BSDDB:
    (handle, gid, styled_text, format, note_type,
     change, marker, private) = data
    text, markup_list = styled_text

    if step == 0:     # Add the primary data:
        n = dj.Note(handle=handle,
                    gramps_id=gid,
                    last_changed=todate(change),
                    private=private,
                    preformatted=format,
                    text=text,
                    marker_type = dj.get_type(dj.MarkerType, marker),
                    note_type = dj.get_type(dj.NoteType, note_type))
        n.save()
        count = 1
        for markup in markup_list:
            markup_code, value, start_stop_list = markup
            m = dj.Markup(note=n, order=count, string=value,
                              start_stop_list=str(start_stop_list))
            m.save()
    elif step == 1:   
        # Nothing for notes to do
        pass 

def export_family(data, step):
    # Unpack from the BSDDB:
    (handle, gid, father_handle, mother_handle,
     child_ref_list, the_type, event_ref_list, media_list,
     attribute_list, lds_seal_list, source_list, note_list,
     change, marker, private) = data

    if step == 0: # Add primary object
        family = dj.Family(handle=handle, gramps_id=gid, 
                      family_rel_type = dj.get_type(dj.FamilyRelType, the_type),
                      last_changed=todate(change), 
                      marker_type = dj.get_type(dj.MarkerType, marker),
                      private=private)
        family.save()
    elif step == 1:
        family = dj.Family.objects.get(handle=handle)
        # father_handle and/or mother_handle can be None
        if father_handle:
            family.father = dj.Person.objects.get(handle=father_handle)
        if mother_handle:
            family.mother = dj.Person.objects.get(handle=mother_handle)
        family.save()
        export_child_ref_list(family, child_ref_list)
        export_note_list(family, note_list)
        export_attribute_list(family, attribute_list)
        export_source_ref_list(family, source_list)
        export_media_ref_list(family, media_list)
        export_event_ref_list(family, event_ref_list)
        export_lds_list(family, lds_seal_list)
    
def export_source(data, step):
    (handle, gid, title,
     author, pubinfo,
     note_list,
     media_list,
     abbrev,
     change, datamap,
     reporef_list,
     marker, private) = data
    if step == 0:
        source = dj.Source(handle=handle, gramps_id=gid, title=title,
                           author=author, pubinfo=pubinfo, abbrev=abbrev,
                           last_changed=todate(change), private=private)
        source.marker_type = dj.get_type(dj.MarkerType, marker)
        source.save()
    elif step == 1:
        source = dj.Source.objects.get(handle=handle)
        export_note_list(source, note_list) 
        export_media_ref_list(source, media_list)
        export_datamap_dict(source, datamap)
        export_repository_ref_list(source, reporef_list)

def export_repository(data, step):
    (handle, gid, the_type, name, note_list,
     address_list, url_list, change, marker, private) = data

    if step == 0:
        repository = dj.Repository(handle=handle,
                                   gramps_id=gid,
                                   marker_type=dj.get_type(dj.MarkerType, marker),
                                   last_changed=todate(change), 
                                   private=private,
                                   repository_type=dj.get_type(dj.RepositoryType, the_type),
                                   name=name)
        repository.save()
    elif step == 1:
        repository = dj.Repository.objects.get(handle=handle)
        export_note_list(repository, note_list)
        export_url_list(repository, url_list)
        export_address_list(repository, address_list)

def export_location(obj, location_data, order):
    if location_data == None: return
    if len(location_data) == 7:
        (street, city, county, state, country, postal, phone) = location_data
        parish = None
    elif len(location_data) == 2:
        ((street, city, county, state, country, postal, phone), parish) = location_data
    else:
        print "ERROR: what kind of location is this?", location_data
    location = dj.Location(street = street,
                           city = city,
                           county = county,
                           state = state,
                           country = country,
                           postal = postal,
                           phone = phone,
                           parish = parish,
                           order = order)
    location.save()
    obj.locations.add(location)
    obj.save()

def export_place(data, step):
    (handle, gid, title, long, lat,
     main_loc, alt_location_list,
     url_list,
     media_list,
     source_list,
     note_list,
     change, marker, private) = data
    if step == 0:
        place = dj.Place(handle=handle, gramps_id=gid, title=title,
                         long=long, lat=lat, last_changed=todate(change),
                         marker_type=dj.get_type(dj.MarkerType, marker),
                         private=private)
        place.save()
    elif step == 1:
        place = dj.Place.objects.get(handle=handle)
        export_url_list(place, url_list)
        export_media_ref_list(place, media_list)
        export_source_ref_list(place, source_list)
        export_note_list(place, note_list) 
        export_location(place, main_loc, 1)
        count = 2
        for loc_data in alt_location_list:
            export_location(place, loc_data, count)
            count + 1

def export_media(data, step):
    (handle, gid, path, mime, desc,
     attribute_list,
     source_list,
     note_list,
     change,
     date,
     marker,
     private) = data
    if step == 0:
        media = dj.Media(handle=handle, gramps_id=gid,
                         path=path, mime=mime, 
                         desc=desc, last_changed=todate(change),
                         marker_type=dj.get_type(dj.MarkerType, marker),
                         private=private)
        export_date(media, date)
        media.save()
    elif step == 1:
        media = dj.Media.objects.get(handle=handle)
        export_note_list(media, note_list) 
        export_source_ref_list(media, source_list)
        export_attribute_list(media, attribute_list)

def export_event(data, step):
    (handle, gid, the_type, date, description, place_handle, 
     source_list, note_list, media_list, attribute_list,
     change, marker, private) = data
    if step == 0:
        event = dj.Event(handle=handle,
                         gramps_id=gid, 
                         event_type=dj.get_type(dj.EventType, the_type),
                         private=private,
                         marker_type=dj.get_type(dj.MarkerType, marker),
                         description=description,
                         last_changed=todate(change))
        export_date(event, date)
        event.save()
    elif step == 1:
        event = dj.Event.objects.get(handle=handle)
        export_place_ref(event, place_handle)
        export_note_list(event, note_list)
        export_attribute_list(event, attribute_list)
        export_media_ref_list(event, media_list)
        export_source_ref_list(event, source_list)

## Main function:

def export_all(database, filename, option_box=None, callback=None):
    if not callable(callback): 
        callback = lambda (percent): None # dummy

    start = time.time()
    total = (database.get_number_of_notes() + 
             database.get_number_of_people() +
             database.get_number_of_events() + 
             database.get_number_of_families() +
             database.get_number_of_repositories() +
             database.get_number_of_places() +
             database.get_number_of_media_objects() +
             database.get_number_of_sources()) * 2 # steps
    count = 0.0
    make_db()

    for step in (0, 1):
        print "Exporting Step %d..." % (step + 1)
        # ---------------------------------
        # Person
        # ---------------------------------
        for person_handle in database.person_map.keys():
            data = database.person_map[person_handle]
            export_person(data, step)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Notes
        # ---------------------------------
        for note_handle in database.note_map.keys():
            data = database.note_map[note_handle]
            export_note(data, step)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Family
        # ---------------------------------
        for family_handle in database.family_map.keys():
            data = database.family_map[family_handle]
            export_family(data, step)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Source
        # ---------------------------------
        for source_handle in database.source_map.keys():
            data = database.source_map[source_handle]
            export_source(data, step)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Event
        # ---------------------------------
        for event_handle in database.event_map.keys():
            data = database.event_map[event_handle]
            export_event(data, step)
            count += 1
            callback(100 * count/total)

        # ---------------------------------
        # Repository
        # ---------------------------------
        for repository_handle in database.repository_map.keys():
            data = database.repository_map[repository_handle]
            export_repository(data, step)
            count += 1
            callback(100 * count/total)
    
        # ---------------------------------
        # Place 
        # ---------------------------------
        for place_handle in database.place_map.keys():
            data = database.place_map[place_handle]
            export_place(data, step)
            count += 1
            callback(100 * count/total)
    
        # ---------------------------------
        # Media
        # ---------------------------------
        for media_handle in database.media_map.keys():
            data = database.media_map[media_handle]
            export_media(data, step)
            count += 1
            callback(100 * count/total)

    total_time = time.time() - start
    msg = ngettext('Export Complete: %d second','Export Complete: %d seconds', total_time ) % total_time
    print msg
    return True

# Future ideas
# Also include meta:
#   Bookmarks
#   Header - researcher info
#   Name formats
#   Namemaps?
#   GRAMPS Version #, date, exporter

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------

class NoFilenameOptions(ExportOptions.WriterOptionBox):
    no_fileselect = True

_name = _('Django Export')
_description = _('Django is a web framework working on a configured database')
_config = (_('Django options'), NoFilenameOptions)

pmgr = PluginManager.get_instance()
plugin = ExportPlugin(name            = _name, 
                      description     = _description,
                      export_function = export_all,
                      extension       = "django",
                      config          = _config )
pmgr.register_plugin(plugin)
