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

"Database Processing/Extract information from names"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import re

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
from QuestionDialog import OkDialog
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
_title_re = re.compile(r"^([A-Za-z][A-Za-z]+\.)\s+(.*)$")
_nick_re = re.compile(r"(.+)\s*[(\"](.*)[)\"]")

#-------------------------------------------------------------------------
#
# Search each name in the database, and compare the firstname against the
# form of "Name (Nickname)".  If it matches, change the first name entry
# to "Name" and add "Nickname" into the nickname field.
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback,parent=None):
    try:
        PatchNames(database,callback,parent)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
# PatchNames
#
#-------------------------------------------------------------------------
class PatchNames:

    def __init__(self,db,callback,parent):
        self.cb = callback
        self.db = db
        self.parent = parent
        self.trans = db.start_transaction()
        self.win_key = self
        self.child_windows = {}
        self.title_list = []
        self.nick_list = []

        for key in self.db.get_person_keys():
        
            person = self.db.get_person_from_handle(key)
            first = person.get_primary_name().get_first_name()
            match = _title_re.match(first)
            if match:
                groups = match.groups()
                self.title_list.append((key,groups[0],groups[1]))
            match = _nick_re.match(first)
            if match:
                groups = match.groups()
                self.nick_list.append((key,groups[0],groups[1]))

        msg = ""

        if self.nick_list or self.title_list:
            self.display()
        else:
            OkDialog(_('No modifications made'),
                     _("No titles or nicknames were found"))

    def toggled(self,cell,path_string):
        path = tuple([int (i) for i in path_string.split(':')])
        row = self.model[path]
        row[0] = not row[0]
        self.model.row_changed(path,row.iter)

    def display(self):

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "patchnames.glade"
        
        self.top = gtk.glade.XML(glade_file,"top","gramps")
        self.window = self.top.get_widget('top')
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_delete_event" : self.on_delete_event
            })
        self.list = self.top.get_widget("list")
        self.label = _('Name and title extraction tool')
        Utils.set_titles(self.window,self.top.get_widget('title'),self.label)

        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)

        r = gtk.CellRendererToggle()
        r.connect('toggled',self.toggled)
        c = gtk.TreeViewColumn(_('Select'),r,active=0)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('ID'),gtk.CellRendererText(),text=1)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Type'),gtk.CellRendererText(),text=2)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Value'),gtk.CellRendererText(),text=3)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Name'),gtk.CellRendererText(),text=4)
        self.list.append_column(c)

        self.list.set_model(self.model)

        self.nick_hash = {}
        self.title_hash = {}
        
        for (id,name,nick) in self.nick_list:
            p = self.db.get_person_from_handle(id)
            iter = self.model.append()
            self.model.set_value(iter,0,1)
            self.model.set_value(iter,1,id)
            self.model.set_value(iter,2,_('Nickname'))
            self.model.set_value(iter,3,nick)
            self.model.set_value(iter,4,p.get_primary_name().get_name())
            self.nick_hash[id] = iter
            
        for (id,title,nick) in self.title_list:
            p = self.db.get_person_from_handle(id)
            iter = self.model.append()
            self.model.set_value(iter,0,1)
            self.model.set_value(iter,1,id)
            self.model.set_value(iter,2,_('Title'))
            self.model.set_value(iter,3,nick)
            self.model.set_value(iter,4,p.get_primary_name().get_name())
            self.title_hash[id] = iter

        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(self.label)
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()
                
    def on_ok_clicked(self,obj):
        for grp in self.nick_list:
            iter = self.nick_hash[grp[0]]
            val = self.model.get_value(iter,0)
            if val:
                p = self.db.get_person_from_handle(grp[0])
                name = p.get_primary_name()
                name.set_first_name(grp[1].strip())
                p.set_nick_name(grp[2].strip())
                self.db.commit_person(p,self.trans)

        for grp in self.title_list:
            iter = self.title_hash[grp[0]]
            val = self.model.get_value(iter,0)
            if val:
                p = self.db.get_person_from_handle(grp[0])
                name = p.get_primary_name()
                name.set_first_name(grp[2].strip())
                name.set_title(grp[1].strip())
                self.db.commit_person(p,self.trans)

        self.db.add_transaction(self.trans,_("Extract information from names"))
        self.close(obj)
        self.cb(1)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Extract information from names"),
    category=_("Database Processing"),
    description=_("Searches the entire database and attempts to "
                  "extract titles and nicknames that may be embedded "
                  "in a person's given name field.")
    )
