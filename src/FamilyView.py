# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
from gtk.gdk import ACTION_COPY, BUTTON1_MASK
from gobject import TYPE_STRING, TYPE_INT

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Sort
import Utils
import GrampsCfg
import AddSpouse
import SelectChild
import DisplayTrace
import Marriage
import ChooseParents
import RelLib
import EditPerson

from gettext import gettext as _
from QuestionDialog import QuestionDialog,WarningDialog

_BORN = _('b.')
_DIED = _('d.')

pycode_tgts = [('child', 0, 0)]

#-------------------------------------------------------------------------
#
# FamilyView
#
#-------------------------------------------------------------------------
class FamilyView:

    def __init__(self,parent):
        self.parent = parent
        self.top = parent.gtop
        self.family = None
        self.cadded = [ 0, 0 ]
        self.init_interface()

    def set_widgets(self,val):
        already_init = self.cadded[val]
        if (val):
            self.ap_data = self.top.get_widget('ap_data2')
            self.swap_btn = self.top.get_widget('swap_btn2')
            self.ap_parents = self.top.get_widget('ap_parents2')
            self.add_spouse_btn = self.top.get_widget('add_spouse2')
            self.sp_parents = self.top.get_widget('sp_parents2')
            self.spouse_list = self.top.get_widget('sp_list2')
            self.select_spouse_btn = self.top.get_widget('select_spouse2')
            self.remove_spouse_btn = self.top.get_widget('remove_spouse2')
            self.child_list = self.top.get_widget('chlist2')
            self.ap_swap_arrow = "Right"
            self.sp_swap_arrow = "Left"
            self.ap_par_arrow = "Down"
            self.sp_par_arrow = "Down"
            self.child_arrow = "Up"
            if not already_init:
                self.top.get_widget('add_parents2').connect('clicked',
                                                            self.add_parents_clicked)
                self.top.get_widget('del_parents2').connect('clicked',
                                                            self.del_parents_clicked)
                self.top.get_widget('add_spparents2').connect('clicked',
                                                              self.add_sp_parents)
                self.top.get_widget('del_spparents2').connect('clicked',
                                                              self.del_sp_parents)
                self.top.get_widget('fam_back2').connect('clicked',
                                                         self.child_back)
                self.top.get_widget('del_child_btn2').connect('clicked',
                                                              self.remove_child_clicked)
                self.top.get_widget('add_child_btn2').connect('clicked',
                                                              self.add_child_clicked)
                self.top.get_widget('select_child2').connect('clicked',
                                                             self.select_child_clicked)
                self.top.get_widget('ap_parents_btn2').connect('clicked',
                                                               self.ap_parents_clicked)
                self.top.get_widget('sp_parents_btn2').connect('clicked',
                                                               self.sp_parents_clicked)
            self.parent.views.get_nth_page(2).show_all()
            if self.parent.views.get_current_page() == 1:
                self.parent.views.set_current_page(2)
            self.parent.views.get_nth_page(1).hide()
        else:
            self.ap_data = self.top.get_widget('ap_data')
            self.swap_btn = self.top.get_widget('swap_spouse_btn')
            self.ap_parents = self.top.get_widget('ap_parents')
            self.add_spouse_btn = self.top.get_widget('add_spouse')
            self.sp_parents = self.top.get_widget('sp_parents')
            self.spouse_list = self.top.get_widget('sp_list')
            self.select_spouse_btn = self.top.get_widget('select_spouse')
            self.remove_spouse_btn = self.top.get_widget('remove_spouse')
            self.child_list = self.top.get_widget('chlist')
            self.ap_swap_arrow = "Down"
            self.sp_swap_arrow = "Up"
            self.ap_par_arrow = "Right"
            self.sp_par_arrow = "Right"
            self.child_arrow = "Left"
            if not already_init:
                self.top.get_widget('add_parents').connect('clicked',
                                                           self.add_parents_clicked)
                self.top.get_widget('del_parents').connect('clicked',
                                                           self.del_parents_clicked)
                self.top.get_widget('add_spparents').connect('clicked',
                                                             self.add_sp_parents)
                self.top.get_widget('del_spparents').connect('clicked',
                                                             self.del_sp_parents)
                self.top.get_widget('fam_back').connect('clicked',
                                                        self.child_back)
                self.top.get_widget('del_child_btn').connect('clicked',
                                                             self.remove_child_clicked)
                self.top.get_widget('add_child_btn').connect('clicked',
                                                             self.add_child_clicked)
                self.top.get_widget('select_child').connect('clicked',
                                                            self.select_child_clicked)
                self.top.get_widget('ap_parents_btn').connect('clicked',
                                                              self.ap_parents_clicked)
                self.top.get_widget('sp_parents_btn').connect('clicked',
                                                              self.sp_parents_clicked)
            self.parent.views.get_nth_page(1).show_all()
            if self.parent.views.get_current_page() == 2:
                self.parent.views.set_current_page(1)
            self.parent.views.get_nth_page(2).hide()

    def init_interface(self):
        fv = GrampsCfg.get_family_view()
        self.set_widgets(fv)

        already_init = self.cadded[fv]
        
        self.ap_model = gtk.ListStore(TYPE_STRING)
        self.ap_data.set_model(self.ap_model)
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.ap_data.append_column(column)
            self.ap_data.connect('button-press-event',self.ap_button_press)
            self.ap_data.connect('key-press-event',self.ap_key_press)

        self.ap_parents_model = gtk.ListStore(TYPE_STRING)
        self.ap_parents.set_model(self.ap_parents_model)
        self.ap_selection = self.ap_parents.get_selection()
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.ap_parents.append_column(column)
            self.ap_parents.connect('button-press-event',self.ap_par_button_press)
            self.ap_parents.connect('key-press-event',self.ap_par_key_press)

        self.sp_parents_model = gtk.ListStore(TYPE_STRING)
        self.sp_parents.set_model(self.sp_parents_model)
        self.sp_selection = self.sp_parents.get_selection()
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.sp_parents.append_column(column)
            self.sp_parents.connect('button-press-event',self.sp_par_button_press)
            self.sp_parents.connect('key-press-event',self.sp_par_key_press)

        self.spouse_model = gtk.ListStore(TYPE_STRING)
        self.spouse_list.set_model(self.spouse_model)
        self.spouse_selection = self.spouse_list.get_selection()
        if not already_init:
            self.spouse_selection.connect('changed',self.spouse_changed)
            self.spouse_list.connect('button-press-event',self.sp_button_press)
            self.spouse_list.connect('key-press-event',self.sp_key_press)
        
        if not already_init:
            column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
            self.spouse_list.append_column(column)
        self.selected_spouse = None

        self.child_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,ACTION_COPY)
        self.child_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.child_list.connect('drag_data_get', self.drag_data_get)
        self.child_list.connect('drag_data_received',self.drag_data_received)
        
        self.child_model = gtk.ListStore(TYPE_INT,   TYPE_STRING,
                                         TYPE_STRING,TYPE_STRING,
                                         TYPE_STRING,TYPE_STRING, 
                                         TYPE_STRING,TYPE_STRING)

        self.child_selection = self.child_list.get_selection()

        if not already_init:
            self.child_list.connect('button-press-event',
                                    self.on_child_list_button_press)
            self.child_list.connect('key-press-event',self.child_key_press)

            self.swap_btn.connect('clicked',self.spouse_swap)
            self.remove_spouse_btn.connect('clicked',self.remove_spouse)
            self.add_spouse_btn.connect('clicked',self.add_spouse)
            self.select_spouse_btn.connect('clicked',self.select_spouse)

        self.child_list.set_model(self.child_model)
        self.child_list.set_search_column(0)
        self.child_selection = self.child_list.get_selection()

        if not already_init:
            Utils.build_columns(self.child_list,
                                [ (' ',30,0), (_('Name'),250,-1), (_('ID'),50,-1),
                                  (_('Gender'),75,-1), (_('Birth date'),150,6),
                                  (_('Status'),100,-1), ('',0,-1) ])
        self.cadded[fv] = 1
        
    def ap_button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.parent.load_person(self.person)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3 and self.person:
            self.build_ap_menu(event)

    def ap_key_press(self,obj,event):
        if event.keyval == gtk.gdk.keyval_from_name("Return") \
                                    and not event.state:
            self.parent.load_person(self.person)
        elif event.keyval == gtk.gdk.keyval_from_name(self.ap_swap_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.spouse_swap(obj)
                
    def sp_key_press(self,obj,event):
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            if self.selected_spouse:
                self.edit_marriage_callback(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Return") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.edit_spouse_callback(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.sp_swap_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.spouse_swap(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.remove_spouse(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.select_spouse(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.add_spouse(obj)

    def ap_par_key_press(self,obj,event):
        if self.person == None:
            return
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            self.edit_ap_relationships(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.ap_par_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.ap_parents_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.del_parents_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.add_parents_clicked(obj)

    def sp_par_key_press(self,obj,event):
        if self.person == None:
            return
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            self.edit_sp_relationships(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.sp_par_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.sp_parents_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.del_sp_parents(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.add_sp_parents(obj)

    def child_key_press(self,obj,event):
        model, iter = self.child_selection.get_selected()
        if not iter:
            return
        id = self.child_model.get_value(iter,7)
        if event.keyval == gtk.gdk.keyval_from_name("Return") and not event.state:
            self.child_rel_by_id(id)
        elif event.keyval == gtk.gdk.keyval_from_name("Return") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.edit_child_callback(obj)
        elif event.keyval == gtk.gdk.keyval_from_name(self.child_arrow) \
                                    and event.state == gtk.gdk.CONTROL_MASK:
            self.child_back(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Delete") and not event.state:
            self.remove_child_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") and not event.state:
            self.select_child_clicked(obj)
        elif event.keyval == gtk.gdk.keyval_from_name("Insert") \
                                    and event.state == gtk.gdk.SHIFT_MASK:
            self.add_child_clicked(obj)

    def build_ap_menu(self,event):
        """Builds the menu with navigation for the active person box"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (_("Add Bookmark"),self.parent.on_add_bookmark_activate,1),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def build_nav_menu(self,event):
        """Builds the menu with navigation (no bookmark)"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def build_parents_nosel_menu(self,event):
        """Builds the menu with navigation and Add parents"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
            (_("Add parents"),self.add_parents_clicked,1),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def build_sp_parents_nosel_menu(self,event):
        """Builds the menu with navigation and Add parents"""
        
        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
            (_("Add parents"),self.add_sp_parents,1),
        ]
        menu = gtk.Menu()
        menu.set_title(_('People Menu'))
        for stock_id,callback,sensitivity in entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)
        menu.popup(None,None,None,event.button,event.time)

    def on_child_list_button_press(self,obj,event):
        model, iter = self.child_selection.get_selected()
        if not iter:
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                self.build_nav_menu(event)
            return
        id = self.child_model.get_value(iter,7)
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.child_rel_by_id(id)
        elif event.state == gtk.gdk.SHIFT_MASK and \
                    event.type == gtk.gdk.BUTTON_PRESS and \
                    event.button == 1:
            self.edit_child_callback(obj)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_child_menu(id,event)

    def build_child_menu(self,id,event):
        """Builds the menu that allows editing operations on the child list"""

        menu = gtk.Menu()
        menu.set_title(_('Child Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected child an active person"), self.child_back),
            (_("Edit the child/parent relationships"), self.child_rel),
            (_("Edit the selected child"),self.edit_child_callback),
            (_("Remove the selected child"),self.remove_child_clicked),
            ]
        for msg,callback in entries:
            Utils.add_menuitem(menu,msg,id,callback)
        menu.popup(None,None,None,event.button,event.time)

    def edit_child_callback(self,obj):
        model, iter = self.child_selection.get_selected()
        if not iter:
            return
        child = self.parent.db.get_person_from_handle(self.child_model.get_value(iter,7))
        try:
            EditPerson.EditPerson(self.parent, child, self.parent.db, self.spouse_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def child_rel(self,obj):
        person = self.parent.db.get_person_from_handle(obj.get_data(Utils.OBJECT))
        SelectChild.EditRel(self.parent.db,person,self.family,self.load_family)
        
    def child_rel_by_id(self,id):
        person = self.parent.db.get_person_from_handle(id)
        SelectChild.EditRel(self.parent.db,person,self.family,self.load_family)

    def spouse_changed(self,obj):
        model, iter = obj.get_selected()
        if not iter:
            self.display_marriage(None)
        else:
            row = model.get_path(iter)
            family_handle = self.person.get_family_handle_list()[row[0]]
            fam = self.parent.db.get_family_from_handle(family_handle)
            self.display_marriage(fam)


    def build_spouse_menu(self,event):

        menu = gtk.Menu()
        menu.set_title(_('Spouse Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected spouse an active person"), self.spouse_swap),
            (_("Edit relationship"), self.edit_marriage_callback),
            (_("Remove the selected spouse"), self.remove_spouse),
            (_("Edit the selected spouse"), self.edit_spouse_callback),
            (_("Set the selected spouse as the preferred spouse"), self.set_preferred_spouse),
            ]
        for msg,callback in entries:
            Utils.add_menuitem(menu,msg,None,callback)
        menu.popup(None,None,None,event.button,event.time)

    def set_preferred_spouse(self,obj):
        if self.selected_spouse:
            self.person.set_preferred_family_handle(self.family)
            trans = self.parent.db.transaction_begin()
            self.parent.db.commit_person(self.person,trans)
            n = self.person.get_primary_name().get_regular_name()
            self.parent.db.transaction_commit(trans,_("Set Preferred Spouse (%s)") % n)
            self.load_family()
            
    def edit_spouse_callback(self,obj):
        if self.selected_spouse:
            try:
                EditPerson.EditPerson(self.parent, self.selected_spouse,
                                      self.parent.db, self.spouse_after_edit)
            except:
                DisplayTrace.DisplayTrace()

    def edit_marriage_callback(self,obj):
        Marriage.Marriage(self.parent, self.family,self.parent.db,
                          self.parent.new_after_edit,
                          self.load_family)

    def sp_button_press(self,obj,event):
        if event.state & gtk.gdk.SHIFT_MASK and \
                    event.type == gtk.gdk.BUTTON_PRESS and \
                    event.button == 1 and self.selected_spouse:
            self.edit_spouse_callback(None)
            
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            if self.selected_spouse:
                self.build_spouse_menu(event)
            else:
                self.build_nav_menu(event)
        elif event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
           if self.person:
               try:
                   if self.selected_spouse:
                       Marriage.Marriage(self.parent,self.family,self.parent.db,
                                         self.parent.new_after_edit,
                                         self.load_family)
                   else:
                       AddSpouse.AddSpouse(self.parent,self.parent.db,self.person,
                                           self.load_family,
                                           self.parent.people_view.redisplay_person_list,
                                           self.family)
               except:
                   DisplayTrace.DisplayTrace()
        
    def select_spouse(self,obj):
        if not self.person:
            return
        try:
            AddSpouse.AddSpouse(self.parent, self.parent.db, self.person,
                                self.load_family,
                                self.parent.people_view.redisplay_person_list)
        except:
            DisplayTrace.DisplayTrace()

    def add_spouse(self,obj):
        person = RelLib.Person()
        if self.person.get_gender() == RelLib.Person.male:
            person.set_gender(RelLib.Person.female)
        else:
            person.set_gender(RelLib.Person.male)
        try:
            EditPerson.EditPerson(self.parent, person, self.parent.db,
                                  self.new_spouse_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def spouse_after_edit(self,epo,trans):
        ap = self.parent.active_person
        if epo:
            self.parent.db.commit_person(epo.person,trans)
            n = epo.person.get_primary_name().get_regular_name()
            self.parent.db.transaction_commit(trans,_("Add Person (%s)") % n)
            self.parent.people_view.remove_from_person_list(epo.person)
            self.parent.people_view.redisplay_person_list(epo.person)

        self.parent.active_person = ap
        self.load_family(self.family)
        
    def new_spouse_after_edit(self,epo,trans):

        self.parent.db.add_person(epo.person,trans)
        self.family = RelLib.Family()
        self.parent.db.add_family(self.family,trans)

        self.parent.people_view.add_to_person_list(epo.person,0)
        self.person.add_family_handle(self.family.get_handle())
        epo.person.add_family_handle(self.family.get_handle())

        self.parent.db.commit_person(epo.person,trans)
        self.parent.db.commit_person(self.person,trans)

        if self.person.get_gender() == RelLib.Person.male:
            self.family.set_mother_handle(epo.person.get_handle())
            self.family.set_father_handle(self.person.get_handle())
        else:	
            self.family.set_father_handle(epo.person.get_handle())
            self.family.set_mother_handle(self.person.get_handle())

        self.parent.db.commit_family(self.family,trans)
        self.load_family(self.family)
        
        m = Marriage.Marriage(self.parent,self.family,self.parent.db,
                              self.parent.new_after_edit,
                              self.load_family)
        m.on_add_clicked()

    def add_child_clicked(self,obj):
        if not self.person:
            return

        person = RelLib.Person()
        autoname = GrampsCfg.get_lastnamegen()
        
        if autoname == 0:
            name = self.north_american(0)
        elif autoname == 2:
            name = self.latin_american(0)
        elif autoname == 3:
            name = self.icelandic(0)
        else:
            name = self.no_name(0)
        person.get_primary_name().set_surname(name[1])
        person.get_primary_name().set_surname_prefix(name[0])

        try:
            EditPerson.EditPerson(self.parent, person, self.parent.db,
                                  self.new_child_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def update_person_list(self,person):
        trans = self.db.transaction_begin()

        if not self.family:
            self.family = RelLib.Family()
            self.parent.db.add_family(self.family,trans)
            person.add_family_handle(self.family.get_handle())
            if person.get_gender() == RelLib.Person.male:
                self.family.set_father_handle(person)
            else:
                self.family.set_mother_handle(person)

        self.family.add_child_handle(person)
        person.add_parent_family_handle(self.family.get_handle(),"Birth","Birth")
        self.parent.update_person_list(person)
        self.load_family(self.family)
        self.db.commit_person(person,trans)
        self.db.commit_family(self.family,trans)
        self.db.transaction_commit(trans,_("Modify family"))
            
    def new_child_after_edit(self,epo,trans):
        
        self.parent.db.add_person(epo.person,trans)
        self.parent.people_view.add_to_person_list(epo.person,0)

        if not self.family:
            self.family = RelLib.Family()
            self.parent.db.add_family(self.family,trans)
            self.person.add_family_handle(self.family.get_handle())
            if self.person.get_gender() == RelLib.Person.male:
                self.family.set_father_handle(self.person.get_handle())
            else:
                self.family.set_mother_handle(self.person.get_handle())

        self.family.add_child_handle(epo.person.get_handle())
        epo.person.add_parent_family_handle(self.family.get_handle(),"Birth","Birth")
        self.parent.db.commit_person(epo.person,trans)
        self.parent.db.commit_family(self.family,trans)
        self.display_marriage(self.family)

    def select_child_clicked(self,obj):
        if not self.person:
            return
        try:
            SelectChild.SelectChild(self.parent, self.parent.db, self.family,
                                    self.person, self.load_family,
                                    self.update_person_list)
        except:
            DisplayTrace.DisplayTrace()

    def remove_child_clicked(self,obj):
        if not self.family or not self.person:
            return

        model, iter = self.child_selection.get_selected()
        if not iter:
            return

        id = self.child_model.get_value(iter,7)
        child = self.parent.db.get_person_from_handle(id)

        trans = self.parent.db.transaction_begin()
        
        self.family.remove_child_handle(child.get_handle())
        child.remove_parent_family_handle(self.family.get_handle())
        
        if len(self.family.get_child_handle_list()) == 0:
            if self.family.get_father_handle() == None:
                self.delete_family_from(self.family.get_mother_handle())
            elif self.family.get_mother_handle() == None:
                self.delete_family_from(self.family.get_father_handle())

        self.parent.db.commit_person(child,trans)
        self.parent.db.commit_family(self.family,trans)
        n = child.get_primary_name().get_regular_name()
        self.parent.db.transaction_commit(trans,_("Remove Child (%s)") % n)
        
        self.load_family()

    def remove_spouse(self,obj):
        if self.selected_spouse:
            nap = GrampsCfg.get_nameof()(self.person)
            nsp = GrampsCfg.get_nameof()(self.selected_spouse)
            QuestionDialog(_('Remove %s as a spouse of %s?') % (nsp,nap),
                           _('Removing a spouse removes the relationship between '
                             'the spouse and the active person. It does not '
                             'remove the spouse from the database'),
                           _('_Remove Spouse'),
                           self.really_remove_spouse)
        elif self.family and not self.family.get_child_handle_list():
            self.really_remove_spouse()
                       
    def really_remove_spouse(self):
        """Delete the currently selected spouse from the family"""
        if self.person == None:
            return

        if self.selected_spouse.get_handle() == self.family.get_father_handle():
            self.family.set_father_handle(None)
        else:
            self.family.set_mother_handle(None)

        trans = self.parent.db.transaction_begin()
        
        if self.selected_spouse:
            self.selected_spouse.remove_family_handle(self.family.get_handle())
            self.parent.db.commit_person(self.selected_spouse,trans)

        self.parent.db.commit_family(self.family,trans)

        if len(self.family.get_child_handle_list()) == 0:
            self.person.remove_family_handle(self.family.get_handle())
            self.parent.db.commit_person(self.person,trans)
            self.parent.db.delete_family(self.family.get_handle(),trans)
            if len(self.person.get_family_handle_list()) > 0:
                handle = self.person.get_family_handle_list()[0]
                family = self.parent.db.find_family_from_handle(handle,trans)
                self.load_family(family)
            else:
                self.load_family(self.family)
        else:
            self.load_family(self.family)
        n = self.person.get_primary_name().get_regular_name()
        self.parent.db.transaction_commit(trans,_("Remove Spouse (%s)") % n)

        if len(self.person.get_family_handle_list()) <= 1:
            self.spouse_selection.set_mode(gtk.SELECTION_NONE)

    def spouse_swap(self,obj):
        if self.selected_spouse:
            self.parent.change_active_person(self.selected_spouse)
            self.load_family(self.family)

    def ap_parents_clicked(self,obj):
        self.change_families(self.person)
            
    def sp_parents_clicked(self,obj):
        self.change_families(self.selected_spouse)

    def change_families(self,person):
        if not person:
            return
        plist = person.get_parent_family_handle_list()

        if len(plist) == 0:
            return
        if len(plist) == 1:
            family_handle,m,r = plist[0]
        else:
            model, iter = self.ap_selection.get_selected()
            path = model.get_path(iter)
            family_handle,m,r = plist[path[0]]
        family = self.parent.db.get_family_from_handle(family_handle)

        if family.get_father_handle():
            person_handle = family.get_father_handle()
        else:
            person_handle = family.get_mother_handle()
        person = self.parent.db.get_person_from_handle(person_handle)
        self.parent.change_active_person(person)

        n = person.get_primary_name().get_name()
        trans = self.parent.db.transaction_begin()
        self.parent.db.commit_family(family,trans)
        self.parent.db.transaction_commit(trans,_("Select Parents (%s)") % n)
        self.load_family(family)

    def clear(self):
        self.spouse_model.clear()
        self.child_model.clear()
        self.sp_parents_model.clear()
        self.ap_parents_model.clear()
        self.ap_model.clear()

    def load_family(self,family=None):

        if self.parent.active_person:
            id = self.parent.active_person.get_handle()
            self.person = self.parent.db.get_person_from_handle(id)
        else:
            self.person = None
            self.clear()
            return

        bd = self.parent.db.get_event_from_handle(self.person.get_birth_handle())
        dd = self.parent.db.get_event_from_handle(self.person.get_death_handle())

        if bd and dd:
            n = "%s [%s]\n\t%s %s\n\t%s %s " % (GrampsCfg.get_nameof()(self.person),
                                                self.person.get_gramps_id(),
                                                _BORN,bd.get_date(),
                                                _DIED,dd.get_date())
        elif bd:
            n = "%s [%s]\n\t%s %s" % (GrampsCfg.get_nameof()(self.person),
                                      self.person.get_gramps_id(),
                                      _BORN,bd.get_date())
        elif dd:
            n = "%s [%s]\n\t%s %s" % (GrampsCfg.get_nameof()(self.person),
                                      self.person.get_gramps_id(),
                                      _DIED,dd.get_date())
        else:
            n = "%s [%s]" % (GrampsCfg.get_nameof()(self.person),
                             self.person.get_gramps_id())

        self.ap_model.clear()
        self.ap_data.get_selection().set_mode(gtk.SELECTION_NONE)
        iter = self.ap_model.append()
        self.ap_model.set(iter,0,n)

        self.selected_spouse = None
        self.spouse_model.clear()
        self.child_model.clear()
        self.sp_parents_model.clear()

        splist = self.person.get_family_handle_list()

        if len(splist) > 1:
            self.spouse_selection.set_mode(gtk.SELECTION_SINGLE)
        else:
            self.spouse_selection.set_mode(gtk.SELECTION_NONE)

        flist = {}

        for f in splist:
            fm = self.parent.db.get_family_from_handle(f)
            
            if fm.get_father_handle() == self.person.get_handle():
                sp_id = fm.get_mother_handle()
            else:
                sp_id = fm.get_father_handle()

            iter = self.spouse_model.append()
            flist[f] = iter
                
            if sp_id:
                sp = self.parent.db.get_person_from_handle(sp_id)
                event = self.find_marriage(fm)
                if event:
                    mdate = " - %s" % event.get_date()
                else:
                    mdate = ""
                v = "%s [%s]\n\t%s%s" % (GrampsCfg.get_nameof()(sp),
                                         sp.get_gramps_id(),
                                         const.family_relations[fm.get_relationship()][0],
                                         mdate)
                self.spouse_model.set(iter,0,v)
            else:
                self.spouse_model.set(iter,0,"%s\n" % _("<double click to add spouse>"))

        if family and family.get_handle() in flist:
            self.display_marriage(family)
            iter = flist[family.get_handle()]
            self.spouse_selection.select_iter(iter)
        elif len(flist) > 0:
            fid = splist[0]
            fam = self.parent.db.get_family_from_handle(fid)
            self.display_marriage(fam)
            iter = flist[fid]
            self.spouse_selection.select_iter(iter)
        else:
            self.display_marriage(None)

        self.update_list(self.ap_parents_model,self.ap_parents,self.person)

    def find_marriage(self,family):
        for event_handle in family.get_event_list():
            if event_handle:
                event = self.parent.db.get_event_from_handle(event_handle)
                if event.get_name() == "Marriage":
                    return event
        return None

    def update_list(self,model,tree,person):
        model.clear()
        sel = None
        selection = tree.get_selection()
        list = person.get_parent_family_handle_list()

        for (f,mrel,frel) in list:
            fam = self.parent.db.get_family_from_handle(f)
            father_handle = fam.get_father_handle()
            mother_handle = fam.get_mother_handle()
            f = self.parent.db.get_person_from_handle(father_handle)
            m = self.parent.db.get_person_from_handle(mother_handle)
            father = self.nameof(_("Father"),f,frel)
            mother = self.nameof(_("Mother"),m,mrel)

            iter = model.append()
            if not sel:
                sel = iter
            v = "%s\n%s" % (father,mother)
            model.set(iter,0,v)
        if len(list) > 1:
            selection.set_mode(gtk.SELECTION_SINGLE)
            selection.select_iter(sel)
        else:
            selection.set_mode(gtk.SELECTION_NONE)
            
    def nameof(self,l,p,mode):
        if p:
            n = GrampsCfg.get_nameof()(p)
            pid = p.get_gramps_id()
            return _("%s: %s [%s]\n\tRelationship: %s") % (l,n,pid,_(mode))
        else:
            return _("%s: unknown") % (l)

    def delete_family_from(self,person):
        trans = self.parent.db.transaction_begin()
        person.remove_family_handle(self.family.get_handle(),trans)
        self.parent.db.delete_family(self.family.get_handle(),trans)
        flist = self.person.get_family_handle_list()
        if len(flist) > 0:
            self.family = flist[0]
        else:
            self.family = None
        n = person.get_primary_name().get_name()
        self.parent.db.transaction_commit(trans,_("Remove from family (%s)") % n)

    def display_marriage(self,family):
        self.child_model.clear()

        if not family:
            self.family = None
            return
        self.family = self.parent.db.get_family_from_handle(family.get_handle())

        if self.family.get_father_handle() == self.person.get_handle():
            sp_id = self.family.get_mother_handle()
            if sp_id:
                self.selected_spouse = self.parent.db.get_person_from_handle(sp_id)
            else:
                self.selected_spouse = None
        else:
            sp_id = self.family.get_father_handle()
            if sp_id:
                self.selected_spouse = self.parent.db.get_person_from_handle(sp_id)
            else:
                self.selected_spouse = None

        if self.selected_spouse:
            self.update_list(self.sp_parents_model,self.sp_parents,
                             self.selected_spouse)

        i = 0
        fiter = None
        child_list = list(self.family.get_child_handle_list())

        self.child_map = {}

        for child_handle in child_list:
            status = _("Unknown")

            child = self.parent.db.get_person_from_handle(child_handle)
            for fam in child.get_parent_family_handle_list():
                if fam[0] == self.family.get_handle():
                    if self.person == self.family.get_father_handle():
                        status = "%s/%s" % (_(fam[2]),_(fam[1]))
                    else:
                        status = "%s/%s" % (_(fam[1]),_(fam[2]))

            iter = self.child_model.append()
            self.child_map[iter] = child.get_handle()
            
            if fiter == None:
                fiter = self.child_model.get_path(iter)
            val = child.get_display_info()
            i += 1
            
            event = self.parent.db.get_event_from_handle(val[3])
            if event:
                dval = event.get_date()
            else:
                dval = u''
            self.child_model.set(iter,0,i,1,val[0],2,val[1],3,val[2],
                                 4,dval,5,status,6,val[6],7,child.get_handle())

    def build_parents_menu(self,family,event):
        """Builds the menu that allows editing operations on the child list"""
        menu = gtk.Menu()
        menu.set_title(_('Parents Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected parents the active family"), self.ap_parents_clicked),
            (_("Edit the child/parent relationships"), self.edit_ap_relationships),
            (_("Add parents"), self.add_parents_clicked),
            (_("Remove parents"),self.del_parents_clicked),
            ]
        for msg,callback in entries:
            Utils.add_menuitem(menu,msg,family,callback)
        menu.popup(None,None,None,event.button,event.time)

    def build_sp_parents_menu(self,family,event):
        """Builds the menu that allows editing operations on the child list"""
        menu = gtk.Menu()
        menu.set_title(_('Spouse Parents Menu'))

        back_sensitivity = self.parent.hindex > 0 
        fwd_sensitivity = self.parent.hindex + 1 < len(self.parent.history)
        nav_entries = [
            (gtk.STOCK_GO_BACK,self.parent.back_clicked,back_sensitivity),
            (gtk.STOCK_GO_FORWARD,self.parent.fwd_clicked,fwd_sensitivity),
            #FIXME: revert to stock item when German gtk translation is fixed
	    #(gtk.STOCK_HOME,self.parent.on_home_clicked,1),
            (_("Home"),self.parent.on_home_clicked,1),
            (None,None,0),
        ]
        for stock_id,callback,sensitivity in nav_entries:
            item = gtk.ImageMenuItem(stock_id)
            #FIXME: remove when German gtk translation is fixed
	    if stock_id == _("Home"):
	    	im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
	    	im.show()
		item.set_image(im)
            if callback:
                item.connect("activate",callback)
            item.set_sensitive(sensitivity)
            item.show()
            menu.append(item)

        entries = [
            (_("Make the selected parents the active family"), self.sp_parents_clicked),
            (_("Edit the child/parent relationships"), self.edit_sp_relationships),
            (_("Add parents"), self.add_sp_parents),
            (_("Remove parents"),self.del_sp_parents),
            ]
        for msg,callback in entries:
            Utils.add_menuitem(menu,msg,family,callback)
        menu.popup(None,None,None,event.button,event.time)

    def edit_ap_relationships(self,obj):
        self.parent_editor(self.person,self.ap_selection)

    def edit_sp_relationships(self,obj):
        self.parent_editor(self.selected_spouse,self.sp_selection)

    def ap_par_button_press(self,obj,event):
        if self.person == None:
            return
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.person,self.ap_selection)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            plist = self.person.get_parent_family_handle_list()

            if len(plist) == 0:
                self.build_parents_nosel_menu(event)
                return
            elif len(plist) == 1:
                family,m,r = plist[0]
            else:
                model, iter = self.ap_selection.get_selected()
                path = model.get_path(iter)
                family,m,r = plist[path[0]]
            self.build_parents_menu(family,event)

    def sp_par_button_press(self,obj,event):
        if self.selected_spouse == None:
            if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
                self.build_nav_menu(event)
            return
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.selected_spouse,self.sp_selection)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            plist = self.selected_spouse.get_parent_family_handle_list()
            if len(plist) == 0:
                self.build_sp_parents_nosel_menu(event)
                return
            elif len(plist) == 1:
                family,m,r = plist[0]
            else:
                model, iter = self.sp_selection.get_selected()
                path = model.get_path(iter)
                family,m,r = plist[path[0]]
            self.build_sp_parents_menu(family,event)

    def add_parents_clicked(self,obj):
        self.parent_add(self.person)

    def add_sp_parents(self,obj):
        if self.selected_spouse:
            self.parent_add(self.selected_spouse)

    def del_parents_clicked(self,obj):
        if len(self.person.get_parent_family_handle_list()) == 0:
            return
        n = GrampsCfg.get_nameof()(self.person)
        QuestionDialog(_('Remove Parents of %s') % n,
                       _('Removing the parents of a person removes the person as a '
                         'child of the parents. The parents are not removed from the '
                         'database, and the relationship between the parents '
                         'is not removed.'),
                       _('_Remove Parents'),
                       self.really_del_parents)
        
    def really_del_parents(self):
        self.parent_deleter(self.person,self.ap_selection)

    def del_sp_parents(self,obj):
        if not self.selected_spouse or len(self.selected_spouse.get_parent_family_handle_list()) == 0:
            return
        n = GrampsCfg.get_nameof()(self.selected_spouse)
        QuestionDialog(_('Remove Parents of %s') % n,
                       _('Removing the parents of a person removes the person as a '
                         'child of the parents. The parents are not removed from the '
                         'database, and the relationship between the parents '
                         'is not removed.'),
                       _('_Remove Parents'),
                       self.really_del_sp_parents)

    def really_del_sp_parents(self):
        self.parent_deleter(self.selected_spouse,self.sp_selection)

    def child_back(self,obj):
        """makes the currently select child the active person"""
        model, iter = self.child_selection.get_selected()
        if iter:
            id = self.child_model.get_value(iter,2)
            child = self.parent.db.get_person_from_gramps_id(id)
            self.parent.change_active_person(child)
            self.load_family()
        else:
            list = self.family.get_child_handle_list()
            if len(list) == 1:
                p = self.parent.db.get_person_from_handle(list[0])
                self.parent.change_active_person(p)
                self.load_family()

    def parent_editor(self,person,selection):
        if not person:
            return

        plist = person.get_parent_family_handle_list()

        if len(plist) == 0:
            return
        elif len(plist) == 1:
            parents,mrel,frel = plist[0]
        else:
            model, iter = selection.get_selected()
            if not iter:
                return

            row = model.get_path(iter)
            parents,mrel,frel = plist[row[0]]

        try:
            ChooseParents.ModifyParents(self.parent.db,person,parents,
                                        self.load_family,
                                        self.parent.full_update,
                                        self.parent.topWindow)
        except:
            DisplayTrace.DisplayTrace()

    def parent_add(self,person):
        if not person:
            return
        try:
            ChooseParents.ChooseParents(self.parent,
                                        self.parent.db,
                                        person,
                                        None,
                                        self.load_family,
                                        self.parent.full_update)
        except:
            DisplayTrace.DisplayTrace()
        
    def parent_deleter(self,person,selection):
        if not person:
            return

        trans = self.parent.db.transaction_begin()
        plist = person.get_parent_family_handle_list()

        if len(plist) == 0:
            return
        if len(plist) == 1:
            person.clear_parent_family_handle_list()
        else:
            model, iter = selection.get_selected()
            if not iter:
                return

            row = model.get_path(iter)
            family_handle = person.get_parent_family_handle_list()[row[0]][0]
            person.remove_parent_family_handle(family_handle)
            fam = self.parent.db.get_family_from_handle(family_handle)

            if len(fam.get_child_handle_list()) == 0:
                father_handle = fam.get_father_handle()
                mother_handle = fam.get_mother_handle()
                if father_handle == None and mother_handle:
                    mother = self.parent.db.find_person_from_handle(mother_handle)
                    mother.remove_family_handle(fam)
                    self.parent.db.commit_person(mother,trans)
                    self.parent.db.delete_family(fam,trans)
                elif mother_handle == None and father_handle:
                    father = self.parent.db.find_person_from_handle(father_handle)
                    father.remove_family_handle(fam,trans)
                    self.parent.db.commit_person(father,trans)
                    self.parent.db.delete_family(fam,trans)

        self.parent.db.commit_person(person,trans)
        n = person.get_primary_name().get_regular_name()
        self.parent.db.transaction_commit(trans,_("Remove Parents (%s)") % n)
        
        self.load_family()

    def drag_data_received(self,widget,context,x,y,sel_data,info,time):
        path = self.child_list.get_path_at_pos(x,y)
        if path == None:
            row = len(self.family.get_child_handle_list())
        else:
            row = path[0][0] -1
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]

            if mytype != 'child':
                return

            s,i = self.child_selection.get_selected()
            if not i:
                return

            spath = s.get_path(i)
            src = spath[0] 
            list = self.family.get_child_handle_list()

            obj = list[src]
            list.remove(obj)
            list.insert(row,obj)
            
            if self.birth_dates_in_order(list) == 0:
                WarningDialog(_("Attempt to Reorder Children Failed"),
                              _("Children must be ordered by their birth dates."))
                return
            self.family.set_child_handle_list(list)
            trans = self.parent.db.transaction_begin()
            self.parent.db.commit_family(self.family,trans)
            self.parent.db.transaction_commit(trans,_('Reorder children'))
            self.display_marriage(self.family)
            
    def drag_data_get(self,widget, context, sel_data, info, time):
        store,iter = self.child_selection.get_selected()
        if not iter:
            return
        id = self.child_model.get_value(iter,2)
        bits_per = 8; # we're going to pass a string
        data = str(('child',id));
        sel_data.set(sel_data.target, bits_per, data)

    def north_american(self,val):
        if self.person.get_gender() == RelLib.Person.male:
            pname = self.person.get_primary_name()
            return (pname.get_surname_prefix(),pname.get_surname())
        elif self.family:
            fid = self.family.get_father_handle()
            f = self.parent.db.get_family_from_handle(fid)
            if f:
                pname = f.get_primary_name()
                return (pname.get_surname_prefix(),pname.get_surname())
        return ("","")

    def no_name(self,val):
        return ("","")

    def latin_american(self,val):
        if self.family:
            father = self.family.get_father_handle()
            mother = self.family.get_mother_handle()
            if not father or not mother:
                return ("","")
            fsn = father.get_primary_name().get_surname()
            msn = mother.get_primary_name().get_surname()
            if not father or not mother:
                return ("","")
            try:
                return ("","%s %s" % (fsn.split()[0],msn.split()[0]))
            except:
                return ("","")
        else:
            return ("","")

    def icelandic(self,val):
        fname = ""
        if self.person.get_gender() == RelLib.Person.male:
            fname = self.person.get_primary_name().get_first_name()
        elif self.family:
            f = self.family.get_father_handle()
            if f:
                fname = f.get_primary_name().get_first_name()
        if fname:
            fname = fname.split()[0]
        if val == 0:
            return ("","%ssson" % fname)
        elif val == 1:
            return ("","%sd�ttir" % fname)
        else:
            return ("","")

    def birth_dates_in_order(self,list):
        """Check any *valid* birthdates in the list to insure that they are in
        numerically increasing order."""
        inorder = 1
        prev_date = "00000000"
        for i in range(len(list)):
            child_handle = list[i]
            child = self.parent.db.get_person_from_handle(child_handle)
            birth_handle = child.get_birth_handle()
            birth = self.parent.db.get_event_from_handle(birth_handle)
            if not birth:
                continue
            bday = birth.get_date_object()
            child_date = Sort.build_sort_date(bday)
            if (child_date == "99999999"):
                continue
            if (prev_date <= child_date):	# <= allows for twins
                prev_date = child_date
            else:
                inorder = 0
        return inorder
