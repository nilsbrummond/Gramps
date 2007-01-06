#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import RelLib

from DisplayTabs import \
     NoteTab,TextTab,GalleryTab,SourceBackRefList,DataEmbedList,RepoEmbedList
from GrampsWidgets import *
from _EditReference import EditReference

#-------------------------------------------------------------------------
#
# EditSourceRef class
#
#-------------------------------------------------------------------------
class EditSourceRef(EditReference):
    def __init__(self, state, uistate, track, source, source_ref, update):

        EditReference.__init__(self, state, uistate, track, source,
                               source_ref, update)

    def _local_init(self):
        
        self.top = gtk.glade.XML(const.gladeFile, "source_ref_edit","gramps")
        
        self.set_window(self.top.get_widget('source_ref_edit'),
                        self.top.get_widget('source_title'),        
                        _('Source Reference Editor'))

        self.define_warn_box(self.top.get_widget("warn_box"))
        self.define_expander(self.top.get_widget("src_expander"))

    def _connect_signals(self):
        self.define_ok_button(self.top.get_widget('ok'),self.ok_clicked)
        self.define_cancel_button(self.top.get_widget('cancel'))

    def _cleanup_on_exit(self):
        # FIXME: the second call was causing the problem, as it was
        # re-setting the whole sref to its original state.
        # that problem is fixed, but _cleanup_on_exit SHOULD NOT be run
        # in close(), because close() is called on OK.
        # Until this is fixed, notes, text and comments are not saved!!!
	self.note_tab.cancel()
	self.text_tab.cancel()
	self.comment_tab.cancel()
        
    def _setup_fields(self):
        self.ref_privacy = PrivacyButton(
            self.top.get_widget('privacy'), self.source_ref, self.db.readonly)

        self.volume = MonitoredEntry(
            self.top.get_widget("volume"), self.source_ref.set_page,
            self.source_ref.get_page, self.db.readonly)
        
        self.gid = MonitoredEntry(
            self.top.get_widget('gid'), self.source.set_gramps_id,
            self.source.get_gramps_id,self.db.readonly)
        
        self.source_privacy = PrivacyButton(
            self.top.get_widget("private"),
            self.source, self.db.readonly)

        print self.top.get_widget('title')

        self.title = MonitoredEntry(
            self.top.get_widget('title'), 
            self.source.set_title,
            self.source.get_title,
            self.db.readonly)
        
        self.abbrev = MonitoredEntry(
            self.top.get_widget('abbrev'), self.source.set_abbreviation,
            self.source.get_abbreviation,self.db.readonly)

        self.author = MonitoredEntry(
            self.top.get_widget('author'), self.source.set_author,
            self.source.get_author,self.db.readonly)
        
        self.pubinfo = MonitoredEntry(
            self.top.get_widget('pub_info'), self.source.set_publication_info,
            self.source.get_publication_info,self.db.readonly)

        self.type_mon = MonitoredMenu(
            self.top.get_widget('confidence'),
            self.source_ref.set_confidence_level,
            self.source_ref.get_confidence_level, [
            (_('Very Low'), RelLib.SourceRef.CONF_VERY_LOW),
            (_('Low'), RelLib.SourceRef.CONF_LOW),
            (_('Normal'), RelLib.SourceRef.CONF_NORMAL),
            (_('High'), RelLib.SourceRef.CONF_HIGH),
            (_('Very High'), RelLib.SourceRef.CONF_VERY_HIGH)],
            self.db.readonly)

        table = self.top.get_widget('table67')
	date_entry = ValidatableMaskedEntry(str)
        date_entry.show()
        table.attach(date_entry, 1, 2, 0, 1)

        self.date = MonitoredDate(
            date_entry,
            self.top.get_widget("date_stat"), 
            self.source_ref.get_date_object(),
            self.uistate,
            self.track,
            self.db.readonly)

    def _create_tabbed_pages(self):
        """
        Creates the notebook tabs and inserts them into the main
        window.
        
        """

        notebook_src = self.top.get_widget('notebook_src')
        notebook_ref = self.top.get_widget('notebook_ref')

        self.note_tab = self._add_tab(
            notebook_src,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source.get_note_object()))
        
        self.gallery_tab = self._add_tab(
            notebook_src,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.source.get_media_list()))
        
        self.data_tab = self._add_tab(
            notebook_src,
            DataEmbedList(self.dbstate, self.uistate, self.track,
                          self.source))
                                       
        self.repo_tab = self._add_tab(
            notebook_src,
            RepoEmbedList(self.dbstate, self.uistate, self.track,
                          self.source.get_reporef_list()))
        
        self.srcref_list = self._add_tab(
            notebook_src,
            SourceBackRefList(self.dbstate,self.uistate, self.track,
                              self.db.find_backlink_handles(self.source.handle),
                              self.enable_warnbox
                              ))

        self.text_tab = self._add_tab(
            notebook_ref,
            TextTab(self.dbstate, self.uistate, self.track,self.source_ref))

        self.comment_tab = self._add_tab(
            notebook_ref,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.source_ref.get_note_object(),_('Comments')))

    def build_menu_names(self,sourceref):
        if self.source:
            source_name = self.source.get_title()
            submenu_label = _('Source: %s')  % source_name
        else:
            submenu_label = _('New Source')
        return (_('Source Reference Editor'),submenu_label)
        
    def ok_clicked(self,obj):

        trans = self.db.transaction_begin()
        if self.source.handle:
            self.db.commit_source(self.source,trans)
            self.db.transaction_commit(trans,_("Modify Source"))
        else:
            self.db.add_source(self.source,trans)
            self.db.transaction_commit(trans,_("Add Source"))

        if self.update:
            self.update(self.source_ref,self.source)

        self.close()
