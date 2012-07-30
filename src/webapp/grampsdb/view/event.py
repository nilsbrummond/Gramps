# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009         Douglas S. Blank <doug.blank@gmail.com>
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
# $Id: utils.py 19637 2012-05-24 17:22:14Z dsblank $
#

""" Views for Person, Name, and Surname """

## Gramps Modules
from webapp.utils import _, boolean, update_last_changed, build_search
from webapp.grampsdb.models import Event, EventType, EventRef, EventRoleType, Person
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface, lookup_role_index
from webapp.dbdjango import DbDjango
from gen.datehandler import displayer, parser

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()
db = DbDjango()
dd = displayer.display
dp = parser.parse

def delete_event(event):
    obj_type = ContentType.objects.get_for_model(Person)
    # First, get those items we need to update:
    event_refs = EventRef.objects.filter(
        ref_object=event,
        object_type=obj_type,
        role_type=get_type_from_name(EventRoleType, "Primary")
        )
    people = []
    for event_ref in event_refs:
        try:
            person = Person.objects.get(id=event_ref.object_id)
        except:
            print "Warning: Corrupt reference in delete_event: %s" % event_ref
            continue
        people.append(person)
    # Remove links to birth/death:
    for person in people:
        if person.death == event:
            person.death = None
            person.save()
        elif person.birth == event:
            person.birth = None
            person.save()
    # Now, delete the event:
    event.delete()
    # Now, update all of the people:
    for person in people:
        recheck_birth_death_refs(person)
        person.save()
        dji.rebuild_cache(person)

def check_event(event):
    obj_type = ContentType.objects.get_for_model(Person)
    # First, get those items we need to update:
    event_refs = EventRef.objects.filter(
        ref_object=event,
        object_type=obj_type,
        role_type=get_type_from_name(EventRoleType, "Primary")
        )
    people = []
    for event_ref in event_refs:
        try:
            person = Person.objects.get(id=event_ref.object_id)
        except:
            print "Warning: Corrupt reference in delete_event: %s" % event_ref
            continue
        recheck_birth_death_refs(person)
        person.save()
        dji.rebuild_cache(person)

def recheck_birth_death_refs(person):
    """
    Reset birth/death references. Need to save later.
    """
    all_events = dji.get_event_ref_list(person)
    obj_type = ContentType.objects.get_for_model(person)
    # Update Birth event references:
    events = EventRef.objects.filter(
        object_id=person.id, 
        object_type=obj_type, 
        role_type=get_type_from_name(EventRoleType, "Primary"),
        ref_object__event_type__val=EventType.BIRTH).order_by("order")
    if events:
        person.birth = events[0].ref_object
        new_index = lookup_role_index(EventType.BIRTH, all_events)
        if person.birth_ref_index != new_index:
            person.birth_ref_index = new_index
    else:
        person.birth = None
        person.birth_ref_index = -1
    # Update Death event references:
    events = EventRef.objects.filter(
        object_id=person.id, 
        object_type=obj_type, 
        role_type=get_type_from_name(EventRoleType, "Primary"),
        ref_object__event_type__val=EventType.DEATH).order_by("order")
    if events:
        person.probably_alive = False
        person.death = events[0].ref_object
        new_index = lookup_role_index(EventType.DEATH, all_events)
        if person.death_ref_index != new_index:
            person.death_ref_index = new_index
    else:
        person.death = None
        person.death_ref_index = -1
        person.probably_alive = True
    
def process_event(request, context, handle, act, add_to=None): # view, edit, save
    """
    Process act on person. Can return a redirect.
    """
    context["tview"] = _("Event")
    context["tviews"] = _("Events")
    context["action"] = "view"
    view_template = "view_event_detail.html"

    if handle == "add":
        act = "add"
    if request.POST.has_key("action"):
        act = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete, share, save-share
    if act == "share":
        item, handle = add_to
        context["pickform"] = PickForm("Pick event", 
                                       Event, 
                                       (),
                                       request.POST)     
        context["object_handle"] = handle
        context["object_type"] = item
        return render_to_response("pick.html", context)
    elif act == "save-share":
        item, handle = add_to 
        pickform = PickForm("Pick event", 
                            Event, 
                            (),
                            request.POST)
        if pickform.data["picklist"]:
            parent_model = dji.get_model(item) # what model?
            parent_obj = parent_model.objects.get(handle=handle) # to add
            ref_handle = pickform.data["picklist"]
            ref_obj = Event.objects.get(handle=ref_handle) 
            dji.add_event_ref_default(parent_obj, ref_obj)
            if item == "person": # then need to recheck birth/death indexes:
                recheck_birth_death_refs(parent_obj)
                parent_obj.save()
            dji.rebuild_cache(parent_obj) # rebuild cache
            return redirect("/%s/%s%s#tab-events" % (item, handle, build_search(request)))
        else:
            context["pickform"] = pickform
            context["object_handle"] = handle
            context["object_type"] = item
            return render_to_response("pick.html", context)
    elif act == "add":
        event = Event(gramps_id=dji.get_next_id(Event, "E"))
        eventform = EventForm(instance=event)
        eventform.model = event
    elif act in ["view", "edit"]: 
        event = Event.objects.get(handle=handle)
        genlibevent = db.get_event_from_handle(handle)
        if genlibevent:
            date = genlibevent.get_date_object()
            event.text = dd(date)
        eventform = EventForm(instance=event)
        eventform.model = event
    elif act == "save": 
        event = Event.objects.get(handle=handle)
        old_place = event.place
        old_place_handle = event.place.handle if event.place else ""
        eventform = EventForm(request.POST, instance=event)
        eventform.model = event
        if eventform.is_valid():
            place_return = request.POST.get("place_return", "")
            is_valid = True
            if place_return == old_place_handle: # same!
                pass
            else: # diff!
                if place_return == "": # clear it
                    event.place = None
                else:
                    try:
                        event.place = Place.objects.get(handle=place_return)
                    except:
                        request.user.message_set.create(message="Please select a valid place")  
                        is_valid = False
            if is_valid:
                update_last_changed(event, request.user.username)
                event = eventform.save()
                # Check any person that might be referenced to see if
                # birth/death issues changed:
                check_event(event)
                event.save()
                dji.rebuild_cache(event)
                act = "view"
            else:
                act = "edit"
        else:
            act = "edit"
    elif act == "create": 
        event = Event(handle=create_id())
        eventform = EventForm(request.POST, instance=event)
        eventform.model = event
        if eventform.is_valid():
            place_return = request.POST.get("place_return", "")
            is_valid = True
            if place_return:
                try:
                    event.place = Place.objects.get(handle=place_return)
                except:
                    request.user.message_set.create(message="Please select a valid place")
                    is_valid = False
            if is_valid:
                update_last_changed(event, request.user.username)
                event = eventform.save()
                dji.rebuild_cache(event)
                if add_to:
                    item, handle = add_to
                    model = dji.get_model(item)
                    obj = model.objects.get(handle=handle)
                    dji.add_event_ref_default(obj, event)
                    if item == "person": # then need to recheck birth/death indexes:
                        recheck_birth_death_refs(obj)
                        obj.save()
                    dji.rebuild_cache(obj)                
                    return redirect("/%s/%s#tab-events" % (item, handle))
                act = "view"
            else:
                act = "add"
        else:
            act = "add"
    elif act == "delete": 
        event = Event.objects.get(handle=handle)
        delete_event(event)
        return redirect("/event/")
    else:
        raise Exception("Unhandled act: '%s'" % act)

    context["eventform"] = eventform
    context["object"] = event
    context["event"] = event
    context["action"] = act
    
    return render_to_response(view_template, context)
