#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  Donald N. Allingham
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

"""
Handles the place view for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import EditPlace
import Utils

from QuestionDialog import QuestionDialog, ErrorDialog
from intl import gettext as _

#-------------------------------------------------------------------------
#
# PlaceView class
#
#-------------------------------------------------------------------------
class PlaceView:
    
    def __init__(self,db,glade,update):
        self.db     = db
        self.glade  = glade
        self.list   = glade.get_widget("place_list")
        self.update = update

        self.column_headers = [
            (_('Place Name'),7,200), (_('ID'),1,50), (_('Church Parish'),8,75),
            (_('City'),9,75), (_('County'),10,75), (_('State'),11,75),
            (_('Country'),12,75), ('',7,0), ('',8,0), ('',9,0), ('',10,0),
            ('',11,0), ('',12,0)]

        self.active = None

        self.id2col = {}
        self.selection = self.list.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        colno = 0
        for title in self.column_headers:
            renderer = gtk.CellRendererText ()
            column = gtk.TreeViewColumn (title[0], renderer, text=colno)
            colno = colno + 1
            column.set_clickable (gtk.TRUE)
            if title[0] == '':
                column.set_visible(gtk.FALSE)
            else:
                column.set_resizable(gtk.TRUE)
                column.set_visible(gtk.TRUE)
            column.set_sort_column_id(title[1])
            column.set_min_width(title[2])
            self.list.append_column(column)

        self.list.set_search_column(0)
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.list.set_model(self.model)
        self.list.get_column(0).clicked()
        self.selection = self.list.get_selection()

    def change_db(self,db):
        self.db = db

    def load_places(self,id=None):
        """Rebuilds the entire place view. This can be very time consuming
        on large databases, and should only be called when absolutely
        necessary"""

        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)
        self.id2col = {}

        for key in self.db.getPlaceKeys():
            val = self.db.getPlaceDisplay(key)
                
            iter = self.model.append()
            self.id2col[key] = iter
            self.model.set(iter,
                           0,   val[0], 1, val[1], 2,   val[2],  3,  val[3],
                           4,   val[4], 5, val[5], 6,   val[6],  7,  val[7],
                           8,   val[8], 9, val[9], 10, val[10], 11,  val[11],
                           12, val[12]
                           )
        self.list.set_model(self.model)
        self.list.get_column(0).clicked()
        
    def goto(self,id):
        self.selection.unselect_all()
        self.selection.select_iter(self.id2col[id])

    def merge(self):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)
        
        if len(mlist) != 2:
            msg = _("Cannot merge people.")
            msg2 = _("Exactly two people must be selected to perform a merge.")
            ErrorDialog(msg,msg2)
        else:
            import MergeData
            MergeData.MergePlaces(self.db,mlist[0],mlist[1],self.load_places)

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            mlist = []
            self.selection.selected_foreach(self.blist,mlist)
            if mlist:
                EditPlace.EditPlace(self,mlist[0],self.update_display)
            return 1
        return 0

    def new_place_after_edit(self,place):
        #self.db.addPlace(place)
        self.update(0)

    def update_display(self,place):
        if place:
            self.db.buildPlaceDisplay(place.getId())
        self.update(0)

    def on_add_place_clicked(self,obj):
        EditPlace.EditPlace(self,RelLib.Place(),self.new_place_after_edit)

    def on_delete_clicked(self,obj):
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for place in mlist:
            for key in self.db.getPersonKeys():
                p = self.db.getPerson(key)
                event_list = [p.getBirth(), p.getDeath()] + p.getEventList()
                if p.getLdsBaptism():
                    event_list.append(p.getLdsBaptism())
                if p.getLdsEndowment():
                    event_list.append(p.getLdsEndowment())
                if p.getLdsSeal():
                    event_list.append(p.getLdsSeal())
                for event in event_list:
                    if event.getPlace() == place:
                        used = 1

            for f in self.db.getFamilyMap().values():
                event_list = f.getEventList()
                if f.getLdsSeal():
                    event_list.append(f.getLdsSeal())
                for event in event_list:
                    if event.getPlace() == place:
                        used = 1

            if used == 1:
                ans = EditPlace.DeletePlaceQuery(place,self.db,self.update_display)
                QuestionDialog(_('Delete %s') %  place.get_title(),
                               _('This place is currently being used by at least one '
                                 'record in the database. Deleting it will remove it '
                                 'from the database and remove it from all records '
                                 'that reference it.'),
                               _('_Delete Place'),
                               ans.query_response)
            else:
                self.db.removePlace(place.getId())
                self.update(0)
                Utils.modified()

    def on_edit_clicked(self,obj):
        """Display the selected places in the EditPlace display"""
        mlist = []
        self.selection.selected_foreach(self.blist,mlist)

        for place in mlist:
            EditPlace.EditPlace(self, place, self.update_display)

    def blist(self,store,path,iter,list):
        id = self.db.getPlace(store.get_value(iter,1))
        list.append(id)
