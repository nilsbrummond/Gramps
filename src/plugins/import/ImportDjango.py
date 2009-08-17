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
def lookup(handle, event_ref_list):
    """
    Find the handle in a unserialized event_ref_list and return code.
    """
    if handle is None:
        return -1
    else:
        count = 0
        for event_ref in event_ref_list:
            (private, note_list, attribute_list, ref, role) = event_ref
            if handle == ref:
                return count
            count += 1
        return -1

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
    # Get methods to retrieve data from the tables
    # -----------------------------------------------

    def get_address_list(self, sql, from_type, from_handle, with_parish):
        results = self.get_links(sql, from_type, from_handle, "address")
        retval = []
        for handle in results:
            result = sql.query("select * from address where handle = ?;",
                               handle)
            retval.append(self.pack_address(sql, result[0], with_parish))
        return retval

    def get_place(self, obj):
        if obj.place:
            return obj.place.handle
        return None

    def get_attribute_list(self, obj):
        # FIXME
        return []
#         handles = self.get_links(sql, from_type, from_handle, "attribute")
#         retval = []
#         for handle in handles:
#             rows = sql.query("select * from attribute where handle = ?;",
#                              handle)
#             for row in rows:
#                 (handle,
#                  the_type0, 
#                  the_type1, 
#                  value, 
#                  private) = row
#                 source_list = self.get_source_ref_list(sql, "attribute", handle)
#                 note_list = self.get_note_list(sql, "attribute", handle)
#                 retval.append((private, source_list, note_list, 
#                                (the_type0, the_type1), value))
#         return retval

    def get_child_ref_list(self, sql, from_type, from_handle):
        results = self.get_links(sql, from_type, from_handle, "child_ref")
        retval = []
        for handle in results:
            rows = sql.query("select * from child_ref where handle = ?;",
                             handle)
            for row in rows:
                (handle, ref, frel0, frel1, mrel0, mrel1, private) = row
                source_list = self.get_source_ref_list(sql, "child_ref", handle)
                note_list = self.get_note_list(sql, "child_ref", handle) 
                retval.append((private, source_list, note_list, ref, 
                               (frel0, frel1), (mrel0, mrel1)))
        return retval

    def get_datamap(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "datamap")
        datamap = {}
        for handle in handles:
            row = sql.query("select * from datamap where handle = ?;",
                            handle)
            if len(row) == 1:
                (handle, key_field, value_field) = row[0]
                datamap[key_field] = value_field
            else:
                print "ERROR: invalid datamap item '%s'" % handle
        return datamap

    def get_event_ref_list(self, sql, from_type, from_handle):
        results = self.get_links(sql, from_type, from_handle, "event_ref")
        retval = []
        for handle in results:
            result = sql.query("select * from event_ref where handle = ?;",
                               handle)
            retval.append(self.pack_event_ref(sql, result[0]))
        return retval

    def get_family_list(self, sql, from_type, from_handle):
        return self.get_links(sql, from_type, from_handle, "family") 

    def get_parent_family_list(self, sql, from_type, from_handle):
        return self.get_links(sql, from_type, from_handle, "parent_family") 

    def get_person_ref_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "person_ref")
        retval = []
        for ref_handle in handles:
            rows = sql.query("select * from person_ref where handle = ?;",
                             ref_handle)
            for row in rows:
                (handle,
                 description,
                 private) = row
                source_list = self.get_source_ref_list(sql, "person_ref", handle)
                note_list = self.get_note_list(sql, "person_ref", handle)
                retval.append((private, 
                               source_list,
                               note_list,
                               handle,
                               description))
        return retval

    def get_location_list(self, sql, from_type, from_handle, with_parish):
        handles = self.get_links(sql, from_type, from_handle, "location")
        results = []
        for handle in handles:
            results += sql.query("""select * from location where handle = ?;""",
                                 handle)
        return [self.pack_location(sql, result, with_parish) for result in results]

    def get_lds_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "lds")
        results = []
        for handle in handles:
            results += sql.query("""select * from lds where handle = ?;""",
                                 handle)
        return [self.pack_lds(sql, result) for result in results]

    def get_event(self, event):
        handle = event.handle
        gid = event.gramps_id
        the_type = tuple(event.event_type)
        description = event.description
        change = time.mktime(event.last_changed.timetuple())
        marker = tuple(event.marker_type)
        private = event.private
        note_list = self.get_note_list(event)           
        source_list = self.get_source_ref_list(event)   
        media_list = self.get_media_list(event)         
        attribute_list = self.get_attribute_list(event)
        date = self.get_date(event)
        place = self.get_place(event)
        return (str(handle), gid, the_type, date, description, place, 
                source_list, note_list, media_list, attribute_list,
                change, marker, private)

    def get_note(self, note):
        if note:
            styled_text = [note.text, []]
            markups = dj.Markup.objects.filter(note=note).order_by("order")
            for markup in markups:
                value = markup.value
                start_stop_list  = markup.start_stop_list
                ss_list = eval(start_stop_list)
                styled_text[1] += [(tuple(markup.markup_type), 
                                    value, ss_list)]
            changed = time.mktime(note.last_changed.timetuple())
            return (str(note.handle), 
                    note.gramps_id, 
                    styled_text, 
                    note.preformatted, 
                    tuple(note.note_type), 
                    changed, 
                    tuple(note.marker_type), 
                    note.private)
        return None

    def get_source_ref_list(self, obj):
        pdb.set_trace()
        obj_type = ContentType.objects.get_for_model(obj)
        sourcerefs = dj.SourceRef.objects.filter(object_id=obj.id, \
                                  object_type=obj_type).order_by("order")
        retval = []
        for sourceref in sourcerefs:
            retval.append(self.get_source_ref(sourceref))
        return retval

    def get_source_ref(self, obj):
        date = self.get_date(obj)
        note_list = self.get_note_list(obj)
        return (date, obj.private, note_list, obj.confidence, 
                obj.ref_object.handle, obj.page)

    def get_media_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        mediarefs = dj.MediaRef.objects.filter(object_id=obj.id, 
                                               object_type=obj_type)
        retval = []
        for mediaref in mediarefs:
            retval.append(self.get_media_ref(mediaref))
        return retval

    def get_media_ref(self, media_ref):
        note_list = self.get_note_list(media_ref)
        attribute_list = self.get_attribute_list(media_ref)
        source_list = self.get_source_ref_list(media_ref)
        return (media_ref.private, source_list, note_list, attribute_list, 
                media_ref.ref_object.handle, (media_ref.x1,
                                              media_ref.y1,
                                              media_ref.x2,
                                              media_ref.y2))
    
    def get_note_list(self, obj):
        obj_type = ContentType.objects.get_for_model(obj)
        noterefs = dj.NoteRef.objects.filter(object_id=obj.id, 
                                             object_type=obj_type)
        retval = []
        for noteref in noterefs:
            retval.append( noteref.ref_object.handle)
        return retval

    def get_repository_ref_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "repository_ref")
        results = []
        for handle in handles:
            results += sql.query("""select * from repository_ref where handle = ?;""",
                                 handle)
        return [self.pack_repository_ref(sql, result) for result in results]

    def get_url_list(self, sql, from_type, from_handle):
        handles = self.get_links(sql, from_type, from_handle, "url")
        results = []
        for handle in handles:
            results += sql.query("""select * from url where handle = ?;""",
                                 handle)
        return [self.pack_url(sql, result) for result in results]

    # ---------------------------------
    # Helpers
    # ---------------------------------

    def pack_address(self, sql, data, with_parish):
        (handle, private) = data 
        source_list = self.get_source_ref_list(sql, "address", handle)
        date_handle = self.get_link(sql, "address", handle, "date")
        date = self.get_date(sql, date_handle)
        note_list = self.get_note_list(sql, "address", handle)
        location = self.get_location(sql, "address", handle, with_parish)
        return (private, source_list, note_list, date, location)

    def pack_lds(self, sql, data):
        (handle, type, place, famc, temple, status, private) = data
        source_list = self.get_source_ref_list(sql, "lds", handle)
        note_list = self.get_note_list(sql, "lds", handle)
        date_handle = self.get_link(sql, "lds", handle, "date")
        date = self.get_date(sql, date_handle)
        return (source_list, note_list, date, type, place,
                famc, temple, status, private)

    def pack_media_ref(self, sql, data):
        (handle,
         ref,
         role0,
         role1,
         role2,
         role3,
         private) = data
        source_list = self.get_source_ref_list(sql, "media_ref", handle)
        note_list = self.get_note_list(sql, "media_ref", handle)
        attribute_list = self.get_attribute_list(sql, "media_ref", handle)
        if role0 == role1 == role2 == role3 == -1:
            role = None
        else:
            role = (role0, role1, role2, role3)
        return (private, source_list, note_list, attribute_list, ref, role)

    def pack_repository_ref(self, sql, data):
        (handle, 
         ref, 
         call_number, 
         source_media_type0,
         source_media_type1,
         private) = data
        note_list = self.get_note_list(sql, "repository_ref", handle)
        return (note_list, 
                ref,
                call_number, 
                (source_media_type0, source_media_type1),
                private)

    def pack_url(self, sql, data):
        (handle, 
         path, 
         desc, 
         type0, 
         type1, 
         private) = data
        return  (private, path, desc, (type0, type1))

    def pack_event_ref(self, sql, data):
        (handle,
         ref,
         role0,
         role1,
         private) = data
        note_list = self.get_note_list(sql, "event_ref", handle)
        attribute_list = self.get_attribute_list(sql, "event_ref", handle)
        role = (role0, role1)
        return (private, note_list, attribute_list, ref, role)

    def pack_source_ref(self, source_ref):
        ref = source_ref.ref_object.handle
        confidence = source_ref.confidence
        page = source_ref.page
        private = source_ref.private
        date = self.get_date(source_ref)
        note_list = self.get_note_list(source_ref)
        return (date, private, note_list, confidence, ref, page)

    def pack_source(self, sql, data):
        (handle, 
         gid, 
         title, 
         author,
         pubinfo,
         abbrev,
         change,
         marker0,
         marker1,
         private) = data
        note_list = self.get_note_list(sql, "source", handle)
        media_list = self.get_media_list(sql, "source", handle)
        reporef_list = self.get_repository_ref_list(sql, "source", handle)
        datamap = {}
        return (handle, gid, title,
                author, pubinfo,
                note_list,
                media_list,
                abbrev,
                change, datamap,
                reporef_list,
                (marker0, marker1), private)

    def get_location(self, sql, from_type, from_handle, with_parish):
        handle = self.get_link(sql, from_type, from_handle, "location")
        if handle:
            results = sql.query("""select * from location where handle = ?;""",
                                handle)
            if len(results) == 1:
                return self.pack_location(sql, results[0], with_parish)

    def get_names(self, sql, from_type, from_handle, primary):
        handles = self.get_links(sql, from_type, from_handle, "name")
        names = []
        for handle in handles:
            results = sql.query("""select * from name where handle = ? and primary_name = ?;""",
                                handle, primary)
            if len(results) > 0:
                names += results
        result = [self.pack_name(sql, name) for name in names]
        if primary:
            if len(result) == 1:
                return result[0]
            elif len(result) == 0:
                return gen.lib.Name().serialize()
            else:
                raise Exception("too many primary names")
        else:
            return result
     
    def pack_name(self, sql, data):
        # unpack name from SQL table:
        (handle,
        primary_name,
        private, 
        first_name, 
        surname, 
        suffix, 
        title, 
        name_type0, 
        name_type1, 
        prefix, 
        patronymic, 
        group_as, 
        sort_as,
        display_as, 
        call) = data
        # build up a GRAMPS object:
        source_list = self.get_source_ref_list(sql, "name", handle)
        note_list = self.get_note_list(sql, "name", handle)
        date_handle = self.get_link(sql, "name", handle, "date")
        date = self.get_date(sql, date_handle)
        return (private, source_list, note_list, date,
                first_name, surname, suffix, title,
                (name_type0, name_type1), prefix, patronymic,
                group_as, sort_as, display_as, call)

    def pack_location(self, sql, data, with_parish):
        (handle,
         street, 
         city, 
         county, 
         state, 
         country, 
         postal, 
         phone,
         parish) = data
        if with_parish:
            return ((street, city, county, state, country, postal, phone), parish)
        else:
            return (street, city, county, state, country, postal, phone)

    def get_place_from_handle(self, sql, ref_handle):
        if ref_handle: 
            place_row = sql.query("select * from place where handle = ?;",
                                  ref_handle)
            if len(place_row) == 1:
                # return just the handle here:
                return place_row[0][0]
            elif len(place_row) == 0:
                print "ERROR: get_place_from_handle('%s'), no such handle." % (ref_handle, )
            else:
                print "ERROR: get_place_from_handle('%s') should be unique; returned %d records." % (ref_handle, len(place_row))
        return ''

    def get_main_location(self, sql, from_handle, with_parish):
        ref_handle = self.get_link(sql, "place_main", from_handle, "location")
        if ref_handle: 
            place_row = sql.query("select * from location where handle = ?;",
                                  ref_handle)
            if len(place_row) == 1:
                return self.pack_location(sql, place_row[0], with_parish)
            elif len(place_row) == 0:
                print "ERROR: get_main_location('%s'), no such handle." % (ref_handle, )
            else:
                print "ERROR: get_main_location('%s') should be unique; returned %d records." % (ref_handle, len(place_row))
        return gen.lib.Location().serialize()

    def get_link(self, sql, from_type, from_handle, to_link):
        """
        Return a link, and return handle.
        """
        if from_handle is None: return
        assert type(from_handle) in [unicode, str], "from_handle is wrong type: %s is %s" % (from_handle, type(from_handle))
        rows = self.get_links(sql, from_type, from_handle, to_link)
        if len(rows) == 1:
            return rows[0]
        elif len(rows) > 1:
            print "ERROR: too many links %s:%s -> %s (%d)" % (from_type, from_handle, to_link, len(rows))
        return None

    def get_links(self, sql, from_type, from_handle, to_link):
        """
        Return a list of handles (possibly none).
        """
        results = sql.query("""select to_handle from link where from_type = ? and from_handle = ? and to_type = ?;""",
                            from_type, from_handle, to_link)
        return [result[0] for result in results]

    def get_date(self, obj):
        if obj: 
            if ((not obj.slash1) and (not obj.slash2) and 
                (obj.day2 == obj.month2 == obj.year2 == 0)):
                dateval = (obj.day1, obj.month1, obj.year1, obj.slash1)
            else:
                dateval = (obj.day1, obj.month1, obj.year1, obj.slash1, 
                           obj.day2, obj.month2, obj.year2, obj.slash2)
            return (obj.calendar, obj.modifier, obj.quality, dateval, 
                    obj.text, obj.sortval, obj.newyear)
        return None

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

#         # ---------------------------------
#         # Process person
#         # ---------------------------------
#         people = sql.query("""select * from person;""")
#         for person in people:
#             if person is None:
#                 continue
#             (handle,        #  0
#              gid,          #  1
#              gender,             #  2
#              death_ref_handle,    #  5
#              birth_ref_handle,    #  6
#              change,             # 17
#              marker0,             # 18
#              marker1,             # 18
#              private,           # 19
#              ) = person
#             primary_name = self.get_names(sql, "person", handle, True) # one
#             alternate_names = self.get_names(sql, "person", handle, False) # list
#             event_ref_list = self.get_event_ref_list(sql, "person", handle)
#             family_list = self.get_family_list(sql, "person", handle)
#             parent_family_list = self.get_parent_family_list(sql, "person", handle)
#             media_list = self.get_media_list(sql, "person", handle)
#             address_list = self.get_address_list(sql, "person", handle, with_parish=False)
#             attribute_list = self.get_attribute_list(sql, "person", handle)
#             urls = self.get_url_list(sql, "person", handle)
#             lds_ord_list = self.get_lds_list(sql, "person", handle)
#             psource_list = self.get_source_ref_list(sql, "person", handle)
#             pnote_list = self.get_note_list(sql, "person", handle)
#             person_ref_list = self.get_person_ref_list(sql, "person", handle)
#             death_ref_index = lookup(death_ref_handle, event_ref_list)
#             birth_ref_index = lookup(birth_ref_handle, event_ref_list)
#             self.db.person_map[str(handle)] = (str(handle),        #  0
#                                                gid,          #  1
#                                                gender,             #  2
#                                                primary_name,       #  3
#                                                alternate_names,    #  4
#                                                death_ref_index,    #  5
#                                                birth_ref_index,    #  6
#                                                event_ref_list,     #  7
#                                                family_list,        #  8
#                                                parent_family_list, #  9
#                                                media_list,         # 10
#                                                address_list,       # 11
#                                                attribute_list,     # 12
#                                                urls,               # 13
#                                                lds_ord_list,       # 14
#                                                psource_list,       # 15
#                                                pnote_list,         # 16
#                                                change,             # 17
#                                                (marker0, marker1), # 18
#                                                private,            # 19
#                                                person_ref_list,    # 20
#                                                )
#             count += 1
#             self.callback(100 * count/total)
#         # ---------------------------------
#         # Process family
#         # ---------------------------------
#         families = sql.query("""select * from family;""")
#         for family in families:
#             (handle,
#              gid,
#              father_handle,
#              mother_handle,
#              the_type0,
#              the_type1,
#              change,
#              marker0,
#              marker1,
#              private) = family

#             child_ref_list = self.get_child_ref_list(sql, "family", handle)
#             event_ref_list = self.get_event_ref_list(sql, "family", handle)
#             media_list = self.get_media_list(sql, "family", handle)
#             attribute_list = self.get_attribute_list(sql, "family", handle)
#             lds_seal_list = self.get_lds_list(sql, "family", handle)
#             source_list = self.get_source_ref_list(sql, "family", handle)
#             note_list = self.get_note_list(sql, "family", handle)

#             self.db.family_map[str(handle)] = (str(handle), gid, 
#                                                father_handle, mother_handle,
#                                                child_ref_list, (the_type0, the_type1), 
#                                                event_ref_list, media_list,
#                                                attribute_list, lds_seal_list, 
#                                                source_list, note_list,
#                                                change, (marker0, marker1), private)

#             count += 1
#             self.callback(100 * count/total)
#         # ---------------------------------
#         # Process repository
#         # ---------------------------------
#         repositories = sql.query("""select * from repository;""")
#         for repo in repositories:
#             (handle, 
#              gid, 
#              the_type0, 
#              the_type1, 
#              name, 
#              change, 
#              marker0, 
#              marker1, 
#              private) = repo

#             note_list = self.get_note_list(sql, "repository", handle)
#             address_list = self.get_address_list(sql, "repository", handle, with_parish=False)
#             urls = self.get_url_list(sql, "repository", handle)

#             self.db.repository_map[str(handle)] = (str(handle), gid, 
#                                                    (the_type0, the_type1),
#                                                    name, note_list,
#                                                    address_list, urls, change, 
#                                                    (marker0, marker1), private)
#             count += 1
#             self.callback(100 * count/total)
#         # ---------------------------------
#         # Process place
#         # ---------------------------------
#         places = sql.query("""select * from place;""")
#         for place in places:
#             count += 1
#             (handle, 
#              gid, 
#              title, 
#              main_loc,
#              long, 
#              lat, 
#              change, 
#              marker0, 
#              marker1, 
#              private) = place

#             # We could look this up by "place_main", but we have the handle:
#             main_loc = self.get_main_location(sql, handle, with_parish=True)
#             alt_location_list = self.get_location_list(sql, "place_alt", handle, 
#                                                        with_parish=True)
#             urls = self.get_url_list(sql, "place", handle)
#             media_list = self.get_media_list(sql, "place", handle)
#             source_list = self.get_source_ref_list(sql, "place", handle)
#             note_list = self.get_note_list(sql, "place", handle)
#             self.db.place_map[str(handle)] = (str(handle), gid, title, long, lat,
#                                               main_loc, alt_location_list,
#                                               urls,
#                                               media_list,
#                                               source_list,
#                                               note_list,
#                                               change, (marker0, marker1), 
#                                               private)
#             self.callback(100 * count/total)
#         # ---------------------------------
#         # Process source
#         # ---------------------------------
#         sources = sql.query("""select * from source;""")
#         for source in sources:
#             (handle, 
#              gid,
#              title,
#              author,
#              pubinfo,
#              abbrev,
#              change,
#              marker0,
#              marker1,
#              private) = source
#             note_list = self.get_note_list(sql, "source", handle)
#             media_list = self.get_media_list(sql, "source", handle)
#             datamap = self.get_datamap(sql, "source", handle)
#             reporef_list = self.get_repository_ref_list(sql, "source", handle)

#             self.db.source_map[str(handle)] = (str(handle), gid, title,
#                                                author, pubinfo,
#                                                note_list,
#                                                media_list,
#                                                abbrev,
#                                                change, datamap,
#                                                reporef_list,
#                                                (marker0, marker1), private)
#             count += 1
#             self.callback(100 * count/total)
#         # ---------------------------------
#         # Process media
#         # ---------------------------------
#         media = sql.query("""select * from media;""")
#         for med in media:
#             (handle, 
#              gid,
#              path,
#              mime,
#              desc,
#              change,
#              marker0,
#              marker1,
#              private) = med

#             attribute_list = self.get_attribute_list(sql, "media", handle)
#             source_list = self.get_source_ref_list(sql, "media", handle)
#             note_list = self.get_note_list(sql, "media", handle)
            
#             date_handle = self.get_link(sql, "media", handle, "date")
#             date = self.get_date(sql, date_handle)

#             self.db.media_map[str(handle)] = (str(handle), gid, path, mime, desc,
#                                               attribute_list,
#                                               source_list,
#                                               note_list,
#                                               change,
#                                               date,
#                                               (marker0, marker1),
#                                               private)
#             count += 1
#             self.callback(100 * count/total)
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

