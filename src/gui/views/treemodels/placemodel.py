#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009-2010  Nick Hall
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2010       Gary Burton
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
# $Id:_PlaceModel.py 9912 2008-01-22 09:17:46Z acraphae $

"""
Place Model.
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import time
import cgi
import logging
_LOG = logging.getLogger(".gui.views.treemodels.placemodel")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ToolTips
import GrampsLocale
from gui.views.treemodels.flatbasemodel import FlatBaseModel
from gui.views.treemodels.treebasemodel import TreeBaseModel

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
COUNTRYLEVELS = {
'default': [_('<Countries>'), _('<States>'), _('<Counties>'), 
            _('<Places>')]
}

#-------------------------------------------------------------------------
#
# PlaceBaseModel
#
#-------------------------------------------------------------------------
class PlaceBaseModel(object):

    HANDLE_COL = 12

    def __init__(self, db):
        self.gen_cursor = db.get_place_cursor
        self.map = db.get_raw_place_data
        self.fmap = [
            self.column_name,
            self.column_id,
            self.column_parish,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.column_latitude,
            self.column_longitude,
            self.column_change,
            self.column_street,
            self.column_handle,
            self.column_tooltip
            ]
        self.smap = [
            self.column_name,
            self.column_id,
            self.column_parish,
            self.column_postal_code,
            self.column_city,
            self.column_county,
            self.column_state,
            self.column_country,
            self.sort_latitude,
            self.sort_longitude,
            self.sort_change,
            self.column_street,
            self.column_handle,
            ]

    def on_get_n_columns(self):
        return len(self.fmap)+1

    def column_handle(self, data):
        return unicode(data[0])

    def column_name(self, data):
        return unicode(data[2])

    def __format_degrees(self, angle, sign_str):
        """
        Format a decimal as degrees, minutes and seconds.
        If the value is not a decimal leave it unformatted.
        """
        try:
            angle = float(angle)
        except ValueError:
            return angle

        if angle >= 0:
            sign = sign_str[0]
        else:
            sign = sign_str[1]
        seconds = abs(int(angle * 60 * 60))
        minutes = seconds / 60
        seconds %= 60
        degrees = minutes / 60
        minutes %= 60

        string = unicode(degrees) + u'\u00b0 ' + \
                 unicode(minutes) + u'\u2032 ' + \
                 unicode(seconds) + u'\u2033 ' + unicode(sign)

        return string
        
    def column_longitude(self, data):
        return self.__format_degrees(data[3], _('EW'))

    def column_latitude(self, data):
        return self.__format_degrees(data[4], _('NS'))

    def sort_longitude(self, data):
        return unicode(data[3])

    def sort_latitude(self, data):
        return unicode(data[4])

    def column_id(self, data):
        return unicode(data[1])

    def column_parish(self, data):
        try:
            return data[5][1]
        except:
            return u''

    def column_street(self, data):
        try:
            return data[5][0][0]
        except:
            return u''

    def column_city(self, data):
        try:
            return data[5][0][1]
        except:
            return u''
        
    def column_county(self, data):
        try:
            return data[5][0][2]
        except:
            return u''
    
    def column_state(self, data):
        try:
            return data[5][0][3]
        except:
            return u''

    def column_country(self, data):
        try:
            return data[5][0][4]
        except:
            return u''

    def column_postal_code(self, data):
        try:
            return data[5][0][5]
        except:
            return u''

    def sort_change(self, data):
        return "%012x" % data[11]
    
    def column_change(self, data):
        return unicode(time.strftime('%x %X',time.localtime(data[11])),
                            GrampsLocale.codeset)

    def column_tooltip(self, data):
        if const.USE_TIPS:
            try:
                t = ToolTips.TipFromFunction(
                    self.db, lambda:
                    self.db.get_place_from_handle(data[0]))
            except:
                log.error("Failed to create tooltip.", exc_info=True)
            return t
        else:
            return u''

#-------------------------------------------------------------------------
#
# PlaceListModel
#
#-------------------------------------------------------------------------
class PlaceListModel(PlaceBaseModel, FlatBaseModel):
    """
    Flat place model.  (Original code in PlaceBaseModel).
    """
    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):

        PlaceBaseModel.__init__(self, db)
        FlatBaseModel.__init__(self, db, scol, order, tooltip_column=13,
                           search=search, skip=skip, sort_map=sort_map)

#-------------------------------------------------------------------------
#
# PlaceTreeModel
#
#-------------------------------------------------------------------------
class PlaceTreeModel(PlaceBaseModel, TreeBaseModel):
    """
    Hierarchical place model.
    """
    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):

        PlaceBaseModel.__init__(self, db)
        TreeBaseModel.__init__(self, db, scol=scol, order=order,
                                tooltip_column=13,
                                search=search, skip=skip, sort_map=sort_map,
                                nrgroups = 3,
                                group_can_have_handle = True)

    def _set_base_data(self):
        """See TreeBaseModel, for place, most have been set in init of
        PlaceBaseModel
        """
        self.number_items = self.db.get_number_of_places
        self.hmap = [self.column_header] + [None]*12

    def get_tree_levels(self):
        """
        Return the headings of the levels in the hierarchy.
        """
        return ['Country', 'State', 'County', 'Place Name']

    def add_row(self, handle, data):
        """
        Add nodes to the node map for a single place.

        handle      The handle of the gramps object.
        data        The object data.
        """
        if data[5] is None:
            # No primary location
            level = [''] * 5
        else:
            #country, state, county, city, street
            level = [data[5][0][i] for i in range(4,-1,-1)]

        node1 = (level[0], )
        node2 = (level[1], level[0])
        node3 = (level[2], level[1], level[0])
        sort_key = self.sort_func(data)

        if not (level[3] or level[4]):
            if level[2]:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, node2, level[1], None, add_parent=False)
                self.add_node(node2, node3, level[2], None, add_parent=False)
                self.add_node(node3, handle, sort_key, handle, add_parent=False)
            elif level[1]:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, node2, level[1], None, add_parent=False)
                self.add_node(node2, handle, level[1], handle, add_parent=False)
            elif level[0]:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, handle, level[0], handle, add_parent=False)
            else:
                self.add_node(None, node1, level[0], None, add_parent=False)
                self.add_node(node1, node2, level[1], None, add_parent=False)
                self.add_node(node2, node3, level[2], None, add_parent=False)
                self.add_node(node3, handle, sort_key, handle, add_parent=False)
               
        else:        
            self.add_node(None, node1, level[0], None, add_parent=False)
            self.add_node(node1, node2, level[1], None, add_parent=False)
            self.add_node(node2, node3, level[2], None, add_parent=False)
            self.add_node(node3, handle, sort_key, handle, add_parent=False)

    def column_name(self, data):
        name = ''
        if data[5] is not None:
            level = [data[5][0][i] for i in range(4,-1,-1)]
            if not (level[3] or level[4]):
                name = unicode(level[2] or level[1] or level[0])
            elif level[3] and level[4]:
                name = unicode(level[3] + ', ' + level[4])
            elif level[3] or level[4]:
                name = unicode(level[3] or level[4])
        if not name:
            name = unicode(data[2])

        if name:
            return cgi.escape(name)
        else:
            return u"<i>%s<i>" % cgi.escape(_("<no name>"))
        
    def column_header(self, node):
        """
        Return a column heading.  This is called for nodes with no associated
        Gramps handle.
        """
        if node.name:
            return '<i>%s</i>' % cgi.escape(node.name)
        else:
            level = len(self.on_get_path(node))
            return '<i>%s</i>' % cgi.escape(COUNTRYLEVELS['default'][level])
