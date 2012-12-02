#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Nick Hall
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from ... import widgets
from .. import build_filter_model
from . import SidebarFilter
from gramps.gen.constfunc import cuni
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.filters.rules.place import (RegExpIdOf, HasIdOf, HasLocation, 
                                     HasNoteRegexp, HasNoteMatchingSubstringOf, 
                                     MatchesFilter)

GenericPlaceFilter = GenericFilterFactory('Place')
#-------------------------------------------------------------------------
#
# PlaceSidebarFilter class
#
#-------------------------------------------------------------------------
class PlaceSidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked

        self.filter_id = widgets.BasicEntry()
        self.filter_title = widgets.BasicEntry()
        self.filter_location = widgets.LocationEntry2(dbstate)
        self.filter_note = widgets.BasicEntry()
        
        self.filter_regex = Gtk.CheckButton(_('Use regular expressions'))
        self.generic = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Place")

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Place')

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Place Name'), self.filter_title)
        self.add_text_entry(_('Location'), self.filter_location)
        self.add_text_entry(_('Note'), self.filter_note)

        self.add_filter_entry(_('Custom filter'), self.generic)
        self.add_regex_entry(self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_title.set_text('')
        self.filter_location.set_text('')
        self.filter_note.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        gid = cuni(self.filter_id.get_text()).strip()
        title = cuni(self.filter_title.get_text()).strip()
        location = self.filter_location.get_handle()
        note = cuni(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
        gen = self.generic.get_active() > 0

        empty = not (gid or title or location or note or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericPlaceFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)
            
            if location:
                rule = HasLocation([location])
                generic_filter.add_rule(rule)
                
            if note:
                if regex:
                    rule = HasNoteRegexp([note])
                else:
                    rule = HasNoteMatchingSubstringOf([note])
                generic_filter.add_rule(rule)

            if self.generic.get_active() != 0:
                model = self.generic.get_model()
                node = self.generic.get_active_iter()
                obj = cuni(model.get_value(node, 0))
                rule = MatchesFilter([obj])
                generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self, name_space):
        if name_space == 'Place':
            all_filter = GenericPlaceFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(rules.place.AllPlaces([]))
            self.generic.set_model(build_filter_model('Place', [all_filter]))
            self.generic.set_active(0)
