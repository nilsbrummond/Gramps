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
#

# $Id$

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import Utils
import PeopleModel
from RelLib import Person
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# SelectChild
#
#-------------------------------------------------------------------------
class SelectChild:

    def __init__(self,parent,db,family,person,redraw,add_person):
        self.parent = parent
        self.db = db
        self.person = person
        self.family = family
        self.redraw = redraw
        self.add_person = add_person
        self.renderer = gtk.CellRendererText()
        self.xml = gtk.glade.XML(const.gladeFile,"select_child","gramps")
    
        if person:
            self.default_name = person.get_primary_name().get_surname().upper()
        else:
            self.default_name = ""

        self.xml.signal_autoconnect({
            "on_save_child_clicked"    : self.on_save_child_clicked,
            "on_child_help_clicked"    : self.on_child_help_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "destroy_passed_object"    : self.close,
            "on_select_child_delete_event" : self.on_delete_event,
            })

        self.select_child_list = {}
        self.top = self.xml.get_widget("select_child")
        title_label = self.xml.get_widget('title')

        Utils.set_titles(self.top,title_label,_('Add Child to Family'))
        
        self.add_child = self.xml.get_widget("childlist")

        if (self.family):
            father = self.db.get_person_from_handle(self.family.get_father_handle())
            mother = self.db.get_person_from_handle(self.family.get_mother_handle())

            if father != None:
                fname = father.get_primary_name().get_name()
                label = _("Relationship to %(father)s") % {
                    'father' : fname
                    }
                self.xml.get_widget("flabel").set_text(label)

            if mother != None:
                mname = mother.get_primary_name().get_name()
                label = _("Relationship to %(mother)s") % {
                    'mother' : mname
                    }
                self.xml.get_widget("mlabel").set_text(label)
        else:
            fname = self.person.get_primary_name().get_name()
            label = _("Relationship to %s") % fname
            
            if self.person.get_gender() == RelLib.Person.male:
                self.xml.get_widget("flabel").set_text(label)
                self.xml.get_widget("mrel_combo").set_sensitive(0)
            else:
                self.xml.get_widget("mlabel").set_text(label)
                self.xml.get_widget("frel_combo").set_sensitive(0)

        self.mrel = self.xml.get_widget("mrel")
        self.frel = self.xml.get_widget("frel")
        self.mrel.set_text(_("Birth"))

        self.frel.set_text(_("Birth"))

        self.refmodel = PeopleModel.PeopleModel(self.db)

        self.add_child.set_model(self.refmodel)
        self.redraw_child_list(2)
        self.add_itself_to_menu()
        self.add_columns(self.add_child)
        self.top.show()

    def add_columns(self,tree):
        column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(gtk.TRUE)        
        #column.set_clickable(gtk.TRUE)
        column.set_min_width(225)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('ID'), self.renderer,text=1)
        column.set_resizable(gtk.TRUE)        
        #column.set_clickable(gtk.TRUE)
        column.set_min_width(75)
        tree.append_column(column)
        column = gtk.TreeViewColumn(_('Birth date'), self.renderer,text=3)
        #column.set_resizable(gtk.TRUE)        
        column.set_clickable(gtk.TRUE)
        tree.append_column(column)

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.top.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self] = self
        self.parent_menu_item = gtk.MenuItem(_('Add Child to Family'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.top.present()

    def on_child_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def redraw_child_list(self,filter):
        return
    
        birth = self.db.find_event_from_handle(self.person.get_birth_handle())
        death = self.db.find_event_from_handle(self.person.get_death_handle())
        if birth:
            bday = birth.get_date_object()
        else:
            bday = None
        if death:
            dday = death.get_date_object()
        else:
            dday = None

        slist = {}
        for f in self.person.get_parent_family_handle_list():
            if f:
                family = self.db.find_family_from_handle(f[0])
                if family.get_father_handle():
                    slist[family.get_father_handle()] = 1
                elif family.get_mother_handle():
                    slist[family.get_mother_handle()] = 1
                for c in family.get_child_handle_list():
                    slist[c] = 1
            
        person_list = []
        for key in self.db.get_person_handles(sort_handles=True):
            person = self.db.get_person_from_handle(key)
            if filter:
                if slist.has_key(key) or person.get_main_parents_family_handle():
                    continue
            
                birth_event = self.db.find_event_from_handle(person.get_birth_handle())
                if birth_event:
                    pbday = birth_event.get_date_object()
                else:
                    pbday = None

                death_event = self.db.find_event_from_handle(person.get_death_handle())
                if death_event:
                    pdday = death_event.get_date_object()
                else:
                    pdday = None
 
                if bday and bday.getYearValid():
                    if pbday and pbday.getYearValid():
                        # reject if child birthdate < parents birthdate + 10
                        if pbday.getLowYear() < bday.getHighYear()+10:
                            continue

                        # reject if child birthdate > parents birthdate + 90
                        if pbday.getLowYear() > bday.getHighYear()+90:
                            continue

                    if pdday and pdday.getYearValid():
                        # reject if child deathdate < parents birthdate+ 10
                        if pdday.getLowYear() < bday.getHighYear()+10:
                            continue
                
                if dday and dday.getYearValid():
                    if pbday and pbday.getYearValid():
                        # reject if childs birth date > parents deathday + 3
                        if pbday.getLowYear() > dday.getHighYear()+3:
                            continue

                    if pdday and pdday.getYearValid():
                        # reject if childs death date > parents deathday + 150
                        if pdday.getLowYear() > dday.getHighYear() + 150:
                            continue
        
            person_list.append(person.get_handle())

        iter = None
        for idval in person_list:
            dinfo = self.db.get_person_from_handle(idval).get_display_info()
            rdata = [dinfo[0],dinfo[1],dinfo[3],dinfo[5],dinfo[6]]
            new_iter = self.refmodel.add(rdata)
            names = dinfo[0].split(',')
            if len(names):
                ln = names[0].upper()
                if self.default_name and ln == self.default_name and not iter:
                    iter = new_iter

        self.refmodel.connect_model()

        if iter:
            self.refmodel.selection.select_iter(iter)
            path = self.refmodel.model.get_path(iter)
            col = self.add_child.get_column(0)
            self.add_child.scroll_to_cell(path,col,1,0.5,0.0)

    def select_function(self,store,path,iter,id_list):
        id_list.append(self.refmodel.get_value(iter,PeopleModel.COLUMN_INT_ID))

    def get_selected_ids(self):
        mlist = []
        self.add_child.get_selection().selected_foreach(self.select_function,mlist)
        return mlist

    def on_save_child_clicked(self,obj):

        idlist = self.get_selected_ids()

        if not idlist or not idlist[0]:
            return

        id = idlist[0]
        select_child = self.db.get_person_from_handle(id)
        if self.person.get_handle() == id:
            ErrorDialog(_("Error selecting a child"),
                        _("A person cannot be linked as his/her own child"),
                        self.top)
            return

        trans = self.db.transaction_begin()
        
        if self.family == None:
            self.family = RelLib.Family()
            self.db.add_family(self.family,trans)
            self.person.add_family_handle(self.family.get_handle())
            if self.person.get_gender() == RelLib.Person.male:
                self.family.set_father_handle(self.person)
            else:	
                self.family.set_mother_handle(self.person)
                
        if id in (self.family.get_father_handle(),self.family.get_mother_handle()):
            ErrorDialog(_("Error selecting a child"),
                        _("A person cannot be linked as his/her own child"),
                        self.top)
            return

        self.family.add_child_handle(select_child.get_handle())
        
        mrel = const.child_relations.find_value(self.mrel.get_text())
        mother = self.db.get_person_from_handle(self.family.get_mother_handle())
        if mother and mother.get_gender() != RelLib.Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.child_relations.find_value(self.frel.get_text())
        father = self.db.get_person_from_handle(self.family.get_father_handle())
        if father and father.get_gender() !=RelLib. Person.male:
            if frel == "Birth":
                frel = "Unknown"

        select_child.add_parent_family_handle(self.family.get_handle(),mrel,frel)

        self.db.commit_person(select_child,trans)
        self.db.commit_family(self.family,trans)
        n = select_child.get_primary_name().get_regular_name()
        self.db.transaction_commit(trans,_("Add Child to Family (%s)") % n)

        self.redraw(self.family)
        self.close(obj)
        
    def on_show_toggled(self,obj):
        self.redraw_child_list(not obj.get_active())

    def north_american(self,val):
        if self.person.get_gender() == Person.male:
            return self.person.get_primary_name().get_surname()
        elif self.family:
            f = self.family.get_father_handle()
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
        if self.person.get_gender() == Person.male:
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

class EditRel:

    def __init__(self,db,child,family,update):
        self.db = db
        self.update = update
        self.child = child
        self.family = family

        self.xml = gtk.glade.XML(const.gladeFile,"editrel","gramps")
        self.top = self.xml.get_widget('editrel')
        self.mdesc = self.xml.get_widget('mrel_desc')
        self.fdesc = self.xml.get_widget('frel_desc')
        self.mentry = self.xml.get_widget('mrel')
        self.fentry = self.xml.get_widget('frel')
        self.mcombo = self.xml.get_widget('mrel_combo')
        self.fcombo = self.xml.get_widget('frel_combo')

        name = child.get_primary_name().get_name()
        Utils.set_titles(self.top,self.xml.get_widget('title'),
                         _('Relationships of %s') % name)

        father = self.db.get_person_from_handle(self.family.get_father_handle())
        mother = self.db.get_person_from_handle(self.family.get_mother_handle())

        if father:
            fname = father.get_primary_name().get_name()
            val = _("Relationship to %(father)s") % {
                'father' : fname }
            self.fdesc.set_text('<b>%s</b>' % val)
            self.fcombo.set_sensitive(1)
        else:
            val = _("Relationship to father")
            self.fdesc.set_text('<b>%s</b>' % val)
            self.fcombo.set_sensitive(0)

        if mother:
            mname = mother.get_primary_name().get_name()
            val = _("Relationship to %(mother)s") % {
                'mother' : mname }
            self.mdesc.set_text('<b>%s</b>' % val)
            self.mcombo.set_sensitive(1)
        else:
            val = _("Relationship to mother")
            self.mdesc.set_text('<b>%s</b>' % val)
            self.mcombo.set_sensitive(0)

        self.xml.signal_autoconnect({
            "on_ok_clicked"    : self.on_ok_clicked,
            "destroy_passed_object"    : self.close
            })

        f = self.child.has_family(self.family.get_handle())
        if f:
            self.fentry.set_text(_(f[2]))
            self.mentry.set_text(_(f[1]))
        
        self.fdesc.set_use_markup(gtk.TRUE)
        self.mdesc.set_use_markup(gtk.TRUE)
        self.top.show()

    def close(self,obj):
        self.top.destroy()

    def on_ok_clicked(self,obj):
        mrel = const.child_relations.find_value(self.mentry.get_text())
        mother = self.db.get_person_from_handle(self.family.get_mother_handle())
        if mother and mother.get_gender() != RelLib.Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.child_relations.find_value(self.fentry.get_text())
        father = self.db.get_person_from_handle(self.family.get_father_handle())
        if father and father.get_gender() !=RelLib. Person.male:
            if frel == "Birth":
                frel = "Unknown"

        self.child.change_parent_family_handle(self.family.get_handle(),mrel,frel)
        trans = self.db.transaction_begin()
        self.db.commit_person(self.child,trans)
        n = self.child.get_primary_name().get_regular_name()
        self.db.transaction_commit(trans,_("Parent Relationships (%s)") % n)
        
        self.update()
        self.top.destroy()
