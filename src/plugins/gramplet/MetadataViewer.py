#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011     Rob G. Healey <robhealey1 [AT] gmail [DOT] com>
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

# *****************************************************************************
# Python Modules
# *****************************************************************************
import os, sys
from datetime import datetime, date
import time

# abilty to escape certain characters from html output...
from xml.sax.saxutils import escape as _html_escape

from fractions import Fraction
#------------------------------------------------
# Gtk/ Gramps modules
#------------------------------------------------
import gtk

from gen.ggettext import gettext as _

# import the pyexiv2 library classes for this addon
_DOWNLOAD_LINK = "http://tilloy.net/dev/pyexiv2/"
pyexiv2_required = True
Min_VERSION_str = "pyexiv2-%d.%d.%d" % (0, 1, 3)
Min_VERSION = (0, 1, 3)
PrefVersion_str = "pyexiv2-%d.%d.%d" % (0, 3, 0)

try:
    import pyexiv2
    if pyexiv2.version_info < Min_VERSION:
        pyexiv2_required = False

except ImportError:
    raise Exception(_("The python binding library, pyexiv2, to exiv2 is not "
        "installed on this computer.\n It can be downloaded from here: %s\n\n"
        "You will need to download at least %s .  I recommend that you download "
        "and install, %s .") % ( _DOWNLOAD_LINK, Min_VERSION_str, PrefVersion_str) )
               
except AttributeError:
    pyexiv2_required = False

if not pyexiv2_required:
    raise Exception(_("The minimum required version for pyexiv2 must be %s \n"
        "or greater.  You may download it from here: %s\n\n  I recommend getting, "
        "%s .") % ( Min_VERSION_str, _DOWNLOAD_LINK, PrefVersion_str) )

# import the required classes for use in this gramplet
from pyexiv2 import ImageMetadata, Rational

from gen.plug import Gramplet
from DateHandler import displayer as _dd

import gen.lib
import Utils
import gen.mime

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# available image types for exiv2
_valid_types = ["jpeg", "exv", "tiff", "dng", "nef", "pef", "pgf", "png", "psd", "jp2", "jpg"]

# set up Exif keys for Image.exif_keys
ImageArtist        = "Exif.Image.Artist"
ImageCopyright    = "Exif.Image.Copyright"
ImageDateTime     = "Exif.Image.DateTime"
ImageLatitude     = "Exif.GPSInfo.GPSLatitude"
ImageLatitudeRef  = "Exif.GPSInfo.GPSLatitudeRef"
ImageLongitude    = "Exif.GPSInfo.GPSLongitude"
ImageLongitudeRef = "Exif.GPSInfo.GPSLongitudeRef"
ImageDescription  = "Exif.Image.ImageDescription"

# set up keys for Image IPTC keys
IptcKeywords = "Iptc.Application2.Keywords"

_DATAMAP = [ImageArtist, ImageCopyright, ImageDateTime,
            ImageLatitude, ImageLatitudeRef, ImageLongitude, ImageLongitudeRef,
            ImageDescription]

_allmonths = list( [_dd.short_months[i], _dd.long_months[i], i] for i in range(1, 13) )

"""
This addon/ gramplet will display an image's metadata if the python library, 
pyexiv2-0.1.3 or greater, is installed?  You may download it from:

http://tilloy.net/dev/pyexiv2/
"""
class MetadataViewer(Gramplet):

    def init(self):

        self.exif_column_width = 15
        self.exif_widgets = {}

        # set all dirty variables to False to begin this gramplet
        self._dirty_image = False

        self.plugin_image = False
        mtype = False

        rows = gtk.VBox()
        for items in [
            ("Artist",          _("Artist/ Author"), None, True,  [],  False, 0, None),
            ("Copyright",       _("Copyright"),    None, True,  [],  False, 0, None),

            # Manual Date
            ("NewDate",         _("Date"),         None, True,   [], False, 0, None),

            # Manual Time
            ("NewTime",         _("Time"),         None, True,   [], False, 0, None),

            # Latitude and Longitude for this image 
            ("Latitude",        _("Latitude"),     None, True,  [],  False, 0, None),
	    ("Longitude",       _("Longitude"),    None, True,  [],  False, 0, None),

            # keywords describing your image
            ("Keywords",        _("Keywords"),     None, True,  [],  False, 0, None) ]:

            pos, text, choices, readonly, callback, dirty, default, source = items
            row = self.make_row(pos, text, choices, readonly, callback, dirty, default, source)
            rows.pack_start(row, False)

        # separator before description textbox
        rows.pack_start( gtk.HSeparator(), True )
	
        # description textbox label
        label = gtk.Label()
        label.set_text("<b><u>%s</u></b>" % _("Description"))
        label.set_use_markup(True)
        rows.pack_start(label, False)

        # description textbox field
        description_box = gtk.TextView()
        description_box.set_wrap_mode(gtk.WRAP_WORD)
        description_box.set_editable(True)
        self.exif_widgets["Description"] = description_box.get_buffer()
        rows.pack_start(description_box, True, True, 0)

        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(rows)
        rows.show_all()

    def post_init(self):
        self.connect_signal("Media", self.update)
        
    def db_changed(self):
        self.dbstate.db.connect('media-update', self.update)
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self): # return false finishes

        # clear all data entry fields
        self.clear_metadata(None)

        active_handle = self.get_active('Media')
        active_media = self.dbstate.db.get_object_from_handle(active_handle)
        if not active_media:
            return

        # get mime type and make sure it is an image?
        mime_type = active_media.get_mime_type()
        mtype = gen.mime.get_description(mime_type)
        if mime_type and mime_type.startswith("image"):
            value, filetype = mime_type.split("/")

            # make sure it is a media type that can be used by exiv2?
            found = any(_type == filetype for _type in _valid_types)
            if not found:
                return
        else:
            # prevent writing or reading from non MIME images
            return

        # make sure media is on the computer?
        image_path = Utils.media_path_full(self.dbstate.db, active_media.get_path() )
        if not os.path.exists(image_path):
            return

        # make sure the file permissions allow reading?
        readable = os.access(image_path, os.R_OK)
        if not readable:
            return

        # define plugin media 
        self.plugin_image = ImageMetadata(image_path)

        # read media metadata
        try:
            self.plugin_image.read()
        except IOError:
            return

        # set up image metadata keys for use in this gramplet
        dataKeyTags = [KeyTag for KeyTag in self.plugin_image.exif_keys if KeyTag in _DATAMAP ]

        for KeyTag in dataKeyTags:

            # Media image Artist
            if KeyTag == ImageArtist:
                self.exif_widgets["Artist"].set_text(
                    self._get_value(KeyTag)
                )

            # media image Copyright
            elif KeyTag == ImageCopyright:
                self.exif_widgets["Copyright"].set_text(
                    self._get_value(KeyTag)
                )

            # media image DateTime
            elif KeyTag == ImageDateTime:

                # date1 may come from the image metadata
                # date2 may come from the Gramps database 
                date1 = self._get_value(KeyTag)
                date2 = active_media.get_date_object()

                use_date = date1 or date2
                if use_date:
                    rdate, rtime = self.process_date(use_date)

                    self.exif_widgets["NewDate"].set_text(rdate)
                    self.exif_widgets["NewTime"].set_text(rtime)

            # Latitude and Latitude Reference
            elif KeyTag == ImageLatitude:

                latitude  =  self._get_value(ImageLatitude)
                longitude = self._get_value(ImageLongitude)

                # if latitude and longitude exist, display them...
                if (latitude and longitude):

                    # split latitude metadata into (degrees, minutes, and seconds) from Rational
                    latdeg, latmin, latsec = rational_to_dms(latitude, self.ValueType)

                    # split longitude metadata into degrees, minutes, and seconds
                    longdeg, longmin, longsec = rational_to_dms(longitude, self.ValueType)

                    latfail = any(value == False for value in [latdeg, latmin, latsec])
                    longfail = any(value == False for value in [longdeg, longmin, longsec])
                    if not latfail and not longfail:

                        # Latitude Direction Reference
                        LatitudeRef = self._get_value(ImageLatitudeRef)

                        self.exif_widgets["Latitude"].set_text( 
                            """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, LatitudeRef)
                        )
    
                        # Longitude Direction Reference
                        LongitudeRef = self._get_value(ImageLongitudeRef)

                        self.exif_widgets["Longitude"].set_text(
                            """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, LongitudeRef)
                        )

            # Image Description Field
            elif KeyTag == ImageDescription:
                self.exif_widgets["Description"].set_text(
                    self._get_value(ImageDescription)
                )

            # image Keywords
            words = ""
            keyWords = self._get_value(IptcKeywords)
            if keyWords:
                index = 1 
                for word in keyWords:
                    words += word
                    if index is not len(keyWords):
                        words += "," 
                    index += 1 
                self.exif_widgets["Keywords"].set_text(words)

    def make_row(self, pos, text, choices=None, readonly=False, callback_list=[],
                 mark_dirty=False, default=0, source=None):

        # Data Entry:
        row = gtk.HBox()
        label = gtk.Label()
        if readonly:
            label.set_text("<b>%s</b>" % text)
            label.set_width_chars(self.exif_column_width)
            label.set_use_markup(True)
            self.exif_widgets[pos] = gtk.Label()
            self.exif_widgets[pos].set_alignment(0.0, 0.5)
            self.exif_widgets[pos].set_use_markup(True)
            label.set_alignment(0.0, 0.5)
            row.pack_start(label, False)
            row.pack_start(self.exif_widgets[pos], False)
        else:
            label.set_text("%s: " % text)
            label.set_width_chars(self.exif_column_width)
            label.set_alignment(1.0, 0.5) 
            if choices == None:
                self.exif_widgets[pos] = gtk.Entry()
                if mark_dirty:
                    self.exif_widgets[pos].connect("changed", self._mark_dirty_image)
                row.pack_start(label, False)
                row.pack_start(self.exif_widgets[pos], True)
            else:
                eventBox = gtk.EventBox()
                self.exif_widgets[pos] = gtk.combo_box_new_text()
                eventBox.add(self.exif_widgets[pos])
                for add_type in choices:
                    self.exif_widgets[pos].append_text(add_type)
                self.exif_widgets[pos].set_active(default) 
                if mark_dirty:
                    self.exif_widgets[pos].connect("changed", self._mark_dirty_image)
                row.pack_start(label, False)
                row.pack_start(eventBox, True)
            if source:
                label = gtk.Label()
                label.set_text("%s: " % source[0])
                label.set_width_chars(self.de_source_width)
                label.set_alignment(1.0, 0.5) 
                self.exif_widgets[source[1] + ":Label"] = label
                self.exif_widgets[source[1]] = gtk.Entry()
                if mark_dirty:
                    self.exif_widgets[source[1]].connect("changed", self._mark_dirty_image)
                row.pack_start(label, False)
                row.pack_start(self.exif_widgets[source[1]], True)
                if not self.show_source:
                    self.exif_widgets[source[1]].hide()
        for name, text, cbtype, callback in callback_list:
            if cbtype == "button":
                label = gtk.Label()
                label.set_text(text)
                self.exif_widgets[pos + ":" + name + ":Label"] = label
                row.pack_start(label, False)
                icon = gtk.STOCK_EDIT
                size = gtk.ICON_SIZE_MENU
                button = gtk.Button()
                image = gtk.Image()
                image.set_from_stock(icon, size)
                button.add(image)
                button.set_relief(gtk.RELIEF_NONE)
                button.connect("clicked", callback)
                self.exif_widgets[pos + ":" + name] = button
                row.pack_start(button, False)
            elif cbtype == "checkbox":
                button = gtk.CheckButton(text)
                button.set_active(True)
                button.connect("clicked", callback)
                self.exif_widgets[pos + ":" + name] = button
                row.pack_start(button, False)
        row.show_all()
        return row

    def clear_metadata(self, obj):
        """
        clears all data fields to nothing
        """

        for key in [ "Artist", "Copyright", "NewDate", "NewTime",
                "Latitude", "Longitude", "Keywords", "Description" ]:
            self.exif_widgets[key].set_text( "" )

    def process_date(self, tmpDate):
        """
        Process the date for read and write processes
        year, month, day, hour, minutes, seconds

        @param: tmpDate = variable to be processed
        """

        year, month, day = False, False, False
        now = time.localtime()
        datetype = tmpDate.__class__

        # get local time for when if it is not available?
        hour, minutes, seconds = now[3:6]

        found = any(datetype == _type for _type in [datetime, date, gen.lib.date.Date])
        if found:

            #ImageDateTime is in datetime.datetime format
            if datetype == datetime:
                year, month, day = tmpDate.year, tmpDate.month, tmpDate.day
                hour, minutes, seconds = tmpDate.hour, tmpDate.minute, tmpDate.second

            # ImageDateTime is in datetime.date format
            elif datetype == date:
                year, month, day = tmpDate.year, tmpDate.month, tmpDate.day

            # ImageDateTime is in gen.lib.date.Date format
            elif datetype == gen.lib.date.Date:
                year, month, day = tmpDate.get_year(), tmpDate.get_month(), tmpDate.get_day()

        # ImageDateTime is in string format
        elif datetype == str:

            # separate date and time from the string
            if "/" in tmpDate:
                rdate, rtime = tmpDate.split("/")
            elif tmpDate.count(" ") == 1:
                rdate, rtime = tmpDate.split(" ")
            else: 
                rdate = tmpDate
                rtime = False

            # split date elements
            year, month, day = _split_values(rdate)

            # split time elements if not False
            if rtime is not False:
                hour, minutes, seconds = _split_values(rtime)
                hour, minutes, seconds = int(hour), int(minutes), int(seconds) 
 
        found = any(value == False for value in [year, month, day] )
        if not found:

            # convert values to integers
            year, day = int(year), int(day)
            month = _return_month(month)
 
            if isinstance(month, int): 
                rdate = "%04d-%s-%02d" % (year, _dd.long_months[month], day)
            elif isinstance(month, str):
                rdate = "%04d-%s-%02d" % (year, month, day)
            rtime = "%02d:%02d:%02d" % (hour, minutes, seconds)

            return rdate, rtime

    def _get_value(self, KeyTag):
        """
        gets the value from the Exif Key, and returns it...

        @param: KeyTag -- image metadata key
        @param: image -- pyexiv2 ImageMetadata instance
        """

        self.ValueType = None
        if "Exif" in KeyTag:
            try:
                KeyValue = self.plugin_image[KeyTag].raw_value
                self.ValueType = 1

            except KeyError:
                KeyValue = self.plugin_image[KeyTag].value
                self.ValueType = 0

            except ValueError:
                KeyValue = ""

            except AttributeError:
                KeyValue = ""

        # Iptc KeyTag
        elif "Iptc" in KeyTag:
            try:
                KeyValue = self.plugin_image[KeyTag].values

            except KeyError:
                KeyValue = "[not set]"

            except ValueError:
                KeyValue = ""

            except AttributeError:
                KeyValue = ""
        return KeyValue

#------------------------------------------------
# Retrieve metadata from image
#------------------------------------------------
def convert_value(value):
    """
    will take a value from the coordinates and return its value
    """

    if isinstance(value, Rational):
        value = value.numerator
    else:
        value = (value.numerator / value.denominator)
    return value

def rational_to_dms(coords, ValueType):
    """
    takes a rational set of coordinates and returns (degrees, minutes, seconds)
    """

    deg, min, sec = False, False, False
    if ValueType is not None:

        if ValueType == 1:
        
            deg, min, sec = coords.split(" ")
            deg, rest = deg.split("/")
            min, rest = min.split("/")
            sec, rest = sec.split("/")
            sec, rest = int(sec), int(rest)

            if rest > 1:
                sec = str( (sec/ rest) )

        elif (ValueType == 0 and isinstance(coords, list) ):
    
            if len(coords) == 3:
                deg, min, sec = coords[0], coords[1], coords[2]
                deg = convert_value(deg)
                min = convert_value(min)
                sec = convert_value(sec)
    return deg, min, sec

#------------------------------------------------
#     Support functions
#------------------------------------------------
def _return_month(month):
    """
    returns either an integer of the month number or the abbreviated month name

    @param: rmonth -- can be one of:
        10, "10", or ( "Oct" or "October" )
    """

    if isinstance(month, str):
        for s, l, i in _allmonths:
            found = any(month == value for value in [s, l])
            if found:
                month = int(i)
                break
    else:
        for s, l, i in _allmonths:
            if str(month) == i:
                month = l
                break
    return month

def _split_values(text):
    """
    splits a variable into its pieces
    """

    if "-" in text:
        separator = "-"
    elif "." in text:
        separator = "."
    elif ":" in text:
        separator = ":"
    else:
        separator = " "
    return [value for value in text.split(separator)]