#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

"""
The AddrEdit module provides the AddressEditor class. This provides a
mechanism for the user to edit address information.
"""

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
import const
import Utils
import Date
import RelLib
import Sources

from DateEdit import DateEdit
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# AddressEditor class
#
#-------------------------------------------------------------------------
class AddressEditor:
    """
    Displays a dialog that allows the user to edit an address.
    """
    def __init__(self,parent,addr,callback,parent_window=None):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        addr - The address that is to be edited
        """
        # Get the important widgets from the glade description
        self.top = gtk.glade.XML(const.dialogFile, "addr_edit","gramps")
        self.window = self.top.get_widget("addr_edit")
        self.addr_start = self.top.get_widget("address_start")
        self.street = self.top.get_widget("street")
        self.city = self.top.get_widget("city")
        self.state = self.top.get_widget("state")
        self.country = self.top.get_widget("country")
        self.postal = self.top.get_widget("postal")
        self.phone = self.top.get_widget("phone")
        self.note_field = self.top.get_widget("addr_note")
        self.priv = self.top.get_widget("priv")
        self.slist = self.top.get_widget("slist")
        self.sources_label = self.top.get_widget("sourcesAddr")
        self.notes_label = self.top.get_widget("noteAddr")
        self.flowed = self.top.get_widget("addr_flowed")
        self.preform = self.top.get_widget("addr_preform")

        self.parent = parent
        self.db = self.parent.db
        self.addr = addr
        self.callback = callback
        name = parent.person.get_primary_name().get_name()
        if name == ", ":
            text = _("Address Editor")
        else:
            text = _("Address Editor for %s") % name
        
        title_label = self.top.get_widget("title")

        Utils.set_titles(self.window,title_label,
                         text,_('Address Editor'))

        if self.addr:
            self.srcreflist = self.addr.get_source_references()
            self.addr_start.set_text(self.addr.get_date())
            self.street.set_text(self.addr.get_street())
            self.city.set_text(self.addr.get_city())
            self.state.set_text(self.addr.get_state())
            self.country.set_text(self.addr.get_country())
            self.postal.set_text(self.addr.get_postal_code())
            self.phone.set_text(self.addr.get_phone())
            self.priv.set_active(self.addr.get_privacy())
            if self.addr.get_note():
                self.note_field.get_buffer().set_text(self.addr.get_note())
                Utils.bold_label(self.notes_label)
            	if addr.get_note_format() == 1:
                    self.preform.set_active(1)
            	else:
                    self.flowed.set_active(1)
        else:
            self.srcreflist = []

        self.sourcetab = Sources.SourceTab(self.srcreflist,self,
                                           self.top, self.window, self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('edit_src'),
                                           self.top.get_widget('del_src'))

        date_stat = self.top.get_widget("date_stat")
        self.date_check = DateEdit(self.addr_start,date_stat)

        self.top.signal_autoconnect({
            "on_switch_page" : self.on_switch_page,
            "on_help_addr_clicked" : self.on_help_clicked
            })

        if parent_window:
            self.window.set_transient_for(parent_window)
        self.val = self.window.run()
        if self.val == gtk.RESPONSE_OK:
            self.ok_clicked()
        self.window.destroy()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')
        self.val = self.window.run()

    def ok_clicked(self):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Address data structure.
        """
        date = unicode(self.addr_start.get_text())
        street = unicode(self.street.get_text())
        city = unicode(self.city.get_text())
        state = unicode(self.state.get_text())
        country = unicode(self.country.get_text())
        phone = unicode(self.phone.get_text())
        postal = unicode(self.postal.get_text())
        b = self.note_field.get_buffer()
        note = unicode(b.get_text(b.get_start_iter(),b.get_end_iter(),gtk.FALSE))
        format = self.preform.get_active()
        priv = self.priv.get_active()
        
        if self.addr == None:
            self.addr = RelLib.Address()
            self.parent.plist.append(self.addr)
        self.addr.set_source_reference_list(self.srcreflist)

        self.update(date,street,city,state,country,postal,phone,note,format,priv)
        self.callback(self.addr)

    def check(self,get,set,data):
        """Compares a data item, updates if necessary, and sets the
        parents lists_changed flag"""
        if get() != data:
            set(data)
            self.parent.lists_changed = 1
            
    def update(self,date,street,city,state,country,postal,phone,note,format,priv):
        """Compares the data items, and updates if necessary"""
        d = Date.Date()
        d.set(date)

        if self.addr.get_date() != d.get_date():
            self.addr.set_date(date)
            self.parent.lists_changed = 1
        
        self.check(self.addr.get_street,self.addr.set_street,street)
        self.check(self.addr.get_country,self.addr.setCountry,country)
        self.check(self.addr.get_city,self.addr.set_city,city)
        self.check(self.addr.get_state,self.addr.set_state,state)
        self.check(self.addr.get_postal_code,self.addr.set_postal_code,postal)
        self.check(self.addr.get_phone,self.addr.set_phone,phone)
        self.check(self.addr.get_note,self.addr.set_note,note)
        self.check(self.addr.get_note_format,self.addr.set_note_format,format)
        self.check(self.addr.get_privacy,self.addr.set_privacy,priv)

    def on_switch_page(self,obj,a,page):
        buf = self.note_field.get_buffer()
        text = unicode(buf.get_text(buf.get_start_iter(),buf.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
