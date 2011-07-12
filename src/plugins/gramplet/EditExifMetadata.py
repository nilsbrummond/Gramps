# -*- coding: utf-8 -*-
#!/usr/bin/python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009-2011 Rob G. Healey <robhealey1@gmail.com>
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

# *****************************************************************************
# Python Modules
# *****************************************************************************
import os
import datetime
import calendar
import time
from PIL import Image

# abilty to escape certain characters from output...
from xml.sax.saxutils import escape as _html_escape

from itertools import chain

from decimal import Decimal, getcontext
getcontext().prec = 6
from fractions import Fraction

import subprocess

# -----------------------------------------------------------------------------
# GTK modules
# -----------------------------------------------------------------------------
import gtk

# -----------------------------------------------------------------------------
# GRAMPS modules
# -----------------------------------------------------------------------------
import GrampsDisplay

from gen.ggettext import gettext as _

from DateHandler import displayer as _dd
from DateHandler import parser as _dp

from gen.plug import Gramplet

from libmetadata import MetadataView, format_datetime
from gui.widgets import ValidatableMaskedEntry
from Errors import ValidationError
from QuestionDialog import WarningDialog, QuestionDialog, OptionDialog

from gen.lib import Date

import gen.mime
import Utils
from PlaceUtils import conv_lat_lon

from gen.db import DbTxn

from ListModel import ListModel

import pyexiv2

# v0.1 has a different API to v0.2 and above
if hasattr(pyexiv2, 'version_info'):
    OLD_API = False
else:
    # version_info attribute does not exist prior to v0.2.0
    OLD_API = True

# define the Exiv2 command...
system_platform = os.sys.platform
if system_platform == "win32":
    EXIV2_FOUND = "exiv2.exe" if Utils.search_for("exiv2.exe") else False
else:
    EXIV2_FOUND = "exiv2" if Utils.search_for("exiv2") else False

#------------------------------------------------
# support functions
#------------------------------------------------

def _parse_datetime(value):
    """
    Parse date and time and return a datetime object.
    """

    value = value.rstrip()
    if not value:
        return None

    if value.find(u':') >= 0:
        # Time part present
        if value.find(u' ') >= 0:
            # Both date and time part
            date_text, time_text = value.rsplit(u' ', 1)
        else:
            # Time only
            date_text = u''
            time_text = value
    else:
        # Date only
        date_text = value
        time_text = u'00:00:00'

    date_part = _dp.parse(date_text)
    try:
        time_part = time.strptime(time_text, '%H:%M:%S')
    except ValueError:
        time_part = None

    if (date_part.get_modifier() == Date.MOD_NONE and time_part is not None):
        return datetime.datetime(
                        date_part.get_year(), 
                        date_part.get_month(),
                        date_part.get_day(),
                        time_part.tm_hour,
                        time_part.tm_min,
                        time_part.tm_sec)
    else:
        return None

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# available image types for exiv2 and pyexiv2
_vtypes = [".bmp", ".dng", ".exv", ".jp2", ".jpeg", ".jpg", ".nef", ".pef", 
    ".pgf", ".png", ".psd", ".srw", ".tiff"]
_VALIDIMAGEMAP = dict( (index, imgtype) for index, imgtype in enumerate(_vtypes) )

# valid converting types for PIL.Image...
# there are more image formats that PIL.Image can convert to,
# but they are not usable in exiv2/ pyexiv2...
_validconvert = [_("<-- Image Types -->"), ".bmp", ".jpg", ".png", ".tiff"]

# set up Exif keys for Image Exif metadata keypairs...
_DATAMAP = {
    "Exif.Image.ImageDescription"  : "Description",
    "Exif.Photo.DateTimeOriginal"  : "Original",
    "Exif.Image.DateTime"          : "Modified",
    "Exif.Photo.DateTimeDigitized" : "Digitized",
    "Exif.Image.Artist"            : "Artist",
    "Exif.Image.Copyright"         : "Copyright",
    "Exif.GPSInfo.GPSLatitudeRef"  : "LatitudeRef",
    "Exif.GPSInfo.GPSLatitude"     : "Latitude",
    "Exif.GPSInfo.GPSLongitudeRef" : "LongitudeRef",
    "Exif.GPSInfo.GPSLongitude"    : "Longitude",
    "Exif.GPSInfo.GPSAltitudeRef"  : "AltitudeRef",
    "Exif.GPSInfo.GPSAltitude"     : "Altitude",
    "Exif.Photo.DateTimeDigitized" : "Digitized" }
_DATAMAP  = dict((key, val) for key, val in _DATAMAP.items() )
_DATAMAP.update( (val, key) for key, val in _DATAMAP.items() )

# define tooltips for all data entry fields...
_TOOLTIPS = {

    # Edit:Message notification area...
    "Edit:Message" : _("User notification area for the Edit Area window."),

    # Media Object Title...
    "MediaTitle" : _("Warning:  Changing this entry will update the Media "
        "object title field in Gramps not Exiv2 metadata."),

    # Description...
    "Description" : _("Provide a short descripion for this image."),

    # Last Change/ Modify Date/ Time...
    "Modified" : _("This is the date/ time that the image was last changed/ modified.\n"
        "Example: 2011-05-24 14:30:00"),

    # Artist...
    "Artist" : _("Enter the Artist/ Author of this image.  The person's name or "
        "the company who is responsible for the creation of this image."),

    # Copyright...
    "Copyright" : _("Enter the copyright information for this image. \n"),

    # Original Date/ Time...
    "Original" : _("The original date/ time when the image was first created/ taken as in a photograph.\n"
        "Example: 1830-01-1 09:30:59"),

    # GPS Latitude coordinates...
    "Latitude" : _("Enter the Latitude GPS coordinates for this image,\n"
        "Example: 43.722965, 43 43 22 N, 38° 38′ 03″ N, 38 38 3"),

    # GPS Longitude coordinates...
    "Longitude" : _("Enter the Longitude GPS coordinates for this image,\n"
        "Example: 10.396378, 10 23 46 E, 105° 6′ 6″ W, -105 6 6"),

    # GPS Altitude (in meters)...
    "Altitude" : _("This is the measurement of Above or Below Sea Level.  It is measured in meters."
        "Example: 200.558, -200.558") }
_TOOLTIPS  = dict( (key, tooltip) for key, tooltip in _TOOLTIPS.items() )

# define tooltips for all buttons...
# common buttons for all images...
_BUTTONTIPS = {

    # Wiki Help button...
    "Help" : _("Displays the Gramps Wiki Help page for 'Edit Image Exif Metadata' "
        "in your web browser."),

    # Edit screen button...
    "Edit" : _("This will open up a new window to allow you to edit/ modify "
        "this image's Exif metadata.\n  It will also allow you to be able to "
        "Save the modified metadata."),

    # Thumbnail Viewing Window button...
    "Thumbnail" : _("Will produce a Popup window showing a Thumbnail Viewing Area"),

    # Image Type button...
    "ImageTypes" : _("Select from a drop- down box the image file type that you "
        "would like to convert your non- Exiv2 compatible media object to."),

    # Convert to different image type...
    "Convert" : _("If your image is not of an image type that can have "
        "Exif metadata read/ written to/from, convert it to a type that can?"),

    # Delete/ Erase/ Wipe Exif metadata button...
    "Delete" : _("WARNING:  This will completely erase all Exif metadata "
        "from this image!  Are you sure that you want to do this?") }

# ------------------------------------------------------------------------
#
# 'Edit Image Exif metadata' Class
#
# ------------------------------------------------------------------------
class EditExifMetadata(Gramplet):
    """
    Special symbols...

    degrees symbol = [Ctrl] [Shift] u \00b0
    minutes symbol =                  \2032
    seconds symbol =                  \2033
    """
    def init(self):

        self.exif_widgets = {}
        self.dates = {}
        self.coordinates = {}

        self.image_path   = False
        self.orig_image   = False
        self.plugin_image = False
        self.media_title = False

        vbox, self.model = self.__build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(vbox)

        self.dbstate.db.connect('media-update', self.update)
        self.connect_signal('Media', self.update)
        self.update()

    def __build_gui(self):
        """
        will display all exif metadata and all buttons.
        """

        main_vbox = gtk.VBox(False, 0)
        main_vbox.set_border_width(10)

        # Displays the file name...
        medialabel = gtk.HBox(False, 0)
        label = self.__create_label("MediaLabel", False, False, False) 
        medialabel.pack_start(label, expand =False)
        main_vbox.pack_start(medialabel, expand =False, fill =True, padding =0)

        # Displays mime type information...
        mimetype = gtk.HBox(False, 0)
        label = self.__create_label("MimeType", False, False, False)
        mimetype.pack_start(label, expand =False)
        main_vbox.pack_start(mimetype, expand =False, fill =True, padding =0)

        # image dimensions...
        imagesize = gtk.HBox(False, 0)
        label = self.__create_label("ImageSize", False, False, False)
        imagesize.pack_start(label, expand =False, fill =False, padding =0)
        main_vbox.pack_start(imagesize, expand =False, fill =True, padding =0)

        # Displays all plugin messages...
        messagearea = gtk.HBox(False, 0)
        label = self.__create_label("MessageArea", False, False, False)
        messagearea.pack_start(label, expand =False)
        main_vbox.pack_start(messagearea, expand =False, fill =True, padding =0)

        # Separator line before the buttons...
        main_vbox.pack_start(gtk.HSeparator(), expand =False, fill =True, padding =5)

        # Thumbnail, ImageType, and Convert buttons...
        new_hbox = gtk.HBox(False, 0)
        main_vbox.pack_start(new_hbox, expand =False, fill =True, padding =5)
        new_hbox.show()

        # Thumbnail button...
        event_box = gtk.EventBox()
        new_hbox.pack_start(event_box, expand =False, fill =True, padding =5)
        event_box.show()

        button = self.__create_button(
            "Thumbnail", _("Thumbnail"), [self.thumbnail_view])
        event_box.add(button)

        # Image Types...
        event_box = gtk.EventBox()
        new_hbox.pack_start(event_box, expand =False, fill =True, padding =5)
        event_box.show()

        combo_box = gtk.combo_box_new_text()
        combo_box.append_text(_validconvert[0])
        combo_box.set_active(0)
        combo_box.set_sensitive(False)
        event_box.add(combo_box)
        self.exif_widgets["ImageTypes"] = combo_box
        combo_box.show()

        # Convert button...
        event_box = gtk.EventBox()
        new_hbox.pack_start(event_box, expand =False, fill =True, padding =5)
        event_box.show()        

        button = self.__create_button(
            "Convert", False, [self.__convert_dialog], gtk.STOCK_CONVERT)
        event_box.add(button)

        # Connect the changed signal to ImageType...
        self.exif_widgets["ImageTypes"].connect("changed", self.changed_cb)

        # Help, Edit, and Delete horizontal box
        new_hbox = gtk.HBox(False, 0)
        main_vbox.pack_start(new_hbox, expand =False, fill =True, padding =5)
        new_hbox.show()

        for (widget, text, callback, icon, is_sensitive) in [
            ("Help",   False, [self.__help_page],   gtk.STOCK_HELP,   True),
            ("Edit",   False, [self.display_edit],  gtk.STOCK_EDIT,   False),
            ("Delete", False, [self.__wipe_dialog], gtk.STOCK_DELETE, False) ]:

            button = self.__create_button(
                widget, text, callback, icon, is_sensitive)
            new_hbox.pack_start(button, expand =False, fill =True, padding =5) 

        self.view = MetadataView()
        main_vbox.pack_start(self.view, expand =False, fill =True, padding =5)

        # Separator line before the Total...
        main_vbox.pack_start(gtk.HSeparator(), expand =False, fill =True, padding =5)

        # number of key/ value pairs shown...
        label = self.__create_label("Total", False, False, False)
        main_vbox.pack_start(label, expand =False, fill =True, padding =5)

        main_vbox.show_all()
        return main_vbox, self.view

    def main(self): # return false finishes
        """
        get the active media, mime type, and reads the image metadata

        *** disable all buttons at first, then activate as needed...
            # Help will never be disabled...
        """

        # deactivate all buttons except Help...
        self.deactivate_buttons(["Convert", "Edit", "ImageTypes", "Delete"])

        db = self.dbstate.db
        imgtype_format = []

        # display all button tooltips only...
        # 1st argument is for Fields, 2nd argument is for Buttons...
        self._setup_widget_tips(fields =False, buttons =True)

        # clears all labels and display area...
        for widget in ["MediaLabel", "MimeType", "ImageSize", "MessageArea", "Total"]:
            self.exif_widgets[widget].set_text("")

        # set Message Ares to Select...
        self.exif_widgets["MessageArea"].set_text(_("Select an image to begin..."))

        active_handle = self.get_active("Media")
        if not active_handle:
            self.set_has_data(False)
            return

        # get image from database...
        self.orig_image = self.dbstate.db.get_object_from_handle(active_handle)
        if not self.orig_image:
            self.set_has_data(False)
            return

        # get file path and attempt to find it?
        self.image_path = Utils.media_path_full(self.dbstate.db,
                self.orig_image.get_path() )

        if not os.path.isfile(self.image_path):
            self.set_has_data(False)
            return

        # display file description/ title...
        self.exif_widgets["MediaLabel"].set_text(_html_escape(
                self.orig_image.get_description() ) )

        # Mime type information...
        mime_type = self.orig_image.get_mime_type()
        self.exif_widgets["MimeType"].set_text(
                gen.mime.get_description(mime_type) )

        # check image read privileges...
        _readable = os.access(self.image_path, os.R_OK)
        if not _readable:
            self.exif_widgets["MessageArea"].set_text(_("Image is NOT readable,\n"
                "Please choose a different image..."))
            return

        # check image write privileges...
        _writable = os.access(self.image_path, os.W_OK)
        if not _writable:
            self.exif_widgets["MessageArea"].set_text(_("Image is NOT writable,\n"
                "You will NOT be able to save Exif metadata...."))
            self.deactivate_buttons(["Edit"])

        # get dirpath/ basename, and extension...
        self.basename, self.extension = os.path.splitext(self.image_path)

        # if image file type is not an Exiv2 acceptable image type,
        # offer to convert it....
        if self.extension not in _VALIDIMAGEMAP.values():

            # Convert message...
            self.exif_widgets["MessageArea"].set_text(_("Please convert this "
                "image type to one of the Exiv2- compatible image types..."))

            imgtype_format = _validconvert
            self._VCONVERTMAP = dict( (index, imgtype) for index, imgtype
                in enumerate(imgtype_format) )

            for index in xrange(1, len(imgtype_format) ):
                self.exif_widgets["ImageTypes"].append_text(imgtype_format[index] )
            self.exif_widgets["ImageTypes"].set_active(0)

            self.activate_buttons(["ImageTypes"])
        else:
            # determine if it is a mime image object?
            if mime_type:
                if mime_type.startswith("image"):

                    # creates, and reads the plugin image instance...
                    self.plugin_image = self.setup_image(self.image_path)
                    if self.plugin_image:

                        # display all Exif tags for this image,
                        # XmpTag and IptcTag has been purposefully excluded...
                        self.__display_exif_tags(self.image_path)

                        if OLD_API:  # prior to pyexiv2-0.2.0
                            try:
                                ttype, tdata = self.plugin_image.getThumbnailData()
                                width, height = tdata.dimensions
                                thumbnail = True

                            except (IOError, OSError):
                                thumbnail = False

                        else:  # pyexiv2-0.2.0 and above...
                            # get image width and height...
                            self.exif_widgets["ImageSize"].show()
                            width, height = self.plugin_image.dimensions
                            self.exif_widgets["ImageSize"].set_text(_("Image "
                                    "Size : %04d x %04d pixels") % (width, height) )

                            # look for the existence of thumbnails?
                            try:
                                previews = self.plugin_image.previews
                                thumbnail = True
                            except (IOError, OSError):
                                thumbnail = False

                        # if a thumbnail exists, then activate the buttton?
                        if thumbnail:
                            self.activate_buttons(["Thumbnail"])

                        # Activate the Edit button...
                        self.activate_buttons(["Edit"])

                # has mime, but not an image...
                else:
                    self.exif_widgets["MessageArea"].set_text(_("Please choose a different image..."))
                    return

            # has no mime...
            else:
                self.exif_widgets["MessageArea"].set_text(_("Please choose a different image..."))
                return

    def db_changed(self):
        self.dbstate.db.connect('media-update', self.update)
        self.connect_signal('Media', self.update)
        self.update()

    def __display_exif_tags(self, full_path =None):
        """
        Display the exif tags.
        """
        # display exif tags in the treeview
        has_data = self.view.display_exif_tags(full_path =self.image_path)

        # update has_data functionality... 
        self.set_has_data(has_data)

        # activate these buttons...
        self.activate_buttons(["Delete"])

    def changed_cb(self, object):
        """
        will show the Convert Button once an Image Type has been selected, and if
            image extension is not an Exiv2- compatible image?
        """

        # get convert image type and check it?
        ext_value = self.exif_widgets["ImageTypes"].get_active()
        if (self.extension not in _VALIDIMAGEMAP.values() and ext_value >= 1):

            # if Convert button is not active, set it to active state
            # so that the user may convert this image?
            if not self.exif_widgets["Convert"].get_sensitive():
                self.activate_buttons(["Convert"])
 
    def _setup_widget_tips(self, fields =None, buttons =None):
        """
        set up widget tooltips...
            * data fields
            * buttons
        """

        # if True, setup tooltips for all Data Entry Fields...
        if fields:
            for widget, tooltip in _TOOLTIPS.items():
                self.exif_widgets[widget].set_tooltip_text(tooltip)

        # if True, setup tooltips for all Buttons...
        if buttons:
            for widget, tooltip in _BUTTONTIPS.items():
                self.exif_widgets[widget].set_tooltip_text(tooltip)

    def setup_image(self, full_path):
        """
        This will:
            * create the plugin image instance if needed,
            * setup the tooltips for the data fields,
            * setup the tooltips for the buttons,
        """

        if OLD_API:  # prior to pyexiv2-0.2.0
            metadata = pyexiv2.Image(full_path)
            try:
                metadata.readMetadata()
            except (IOError, OSError):
                self.set_has_data(False)
                return 

        else:  # pyexiv2-0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except (IOError, OSError):
                self.set_has_data(False)
                return

        return metadata

    def update_has_data(self):
        active_handle = self.get_active('Media')
        active = self.dbstate.db.get_object_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))

    def get_has_data(self, media):
        """
        Return True if the gramplet has data, else return False.
        """

        if media is None:
            return False

        full_path = Utils.media_path_full(self.dbstate.db, media.get_path() )
        return self.view.get_has_data(full_path)

    def __create_button(self, pos, text, callback =[], icon =False, sensitive =False):
        """
        creates and returns a button for display
        """
        if (icon and not text):
            button = gtk.Button(stock =icon)
        else:
            button = gtk.Button(text)

        if callback is not []:
            for call_ in callback:
                button.connect("clicked", call_)

        # attach a addon widget to the button for later manipulation...
        self.exif_widgets[pos] = button

        if not sensitive:
            button.set_sensitive(False)

        button.show()
        return button

    def __create_label(self, widget, text, width, height, wrap =True):
        """
        creates a label for this addon.
        """
        label = gtk.Label()

        if text:
            label.set_text(text)
        label.set_alignment(0.0, 0.0)

        if wrap:
            label.set_line_wrap(True)

        if (width and height):
            label.set_size_request(width, height)

        if widget:
            self.exif_widgets[widget] = label

        label.show()
        return label

    def thumbnail_view(self, object):
        """
        will allow a display area for a thumbnail pop-up window.
        """
 
        tip = _("Click Close to close this Thumbnail View Area.")

        self.tbarea = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.tbarea.tooltip = tip
        self.tbarea.set_title(_("Thumbnail View Area"))
        self.tbarea.set_default_size((width + 40), (height + 40))
        self.tbarea.set_border_width(10)
        self.tbarea.connect('destroy', lambda w: self.tbarea.destroy() )

        pbloader, width, height = self.__get_thumbnail_data()

        new_vbox = self.build_thumbnail_gui(pbloader, width, height)
        self.tbarea.add(new_vbox)
        self.tbarea.show()

    def __get_thumbnail_data(self):
        """
        returns the thumbnail width and height from the active media object if there is any?
        """

        dirpath, filename = os.path.split(self.image_path)
        pbloader, width, height = [False]*3

        if OLD_API:  # prior to pyexiv2-0.2.0
            try:
               ttype, tdata = self.plugin_image.getThumbnailData()
               width, height = tdata.dimensions
            except (IOError, OSError):
                print(_('Error: %s does not contain an EXIF thumbnail.') % filename)
                self.close_window(self.tbarea)

            # Create a GTK pixbuf loader to read the thumbnail data
            pbloader = gtk.gdk.PixbufLoader()
            pbloader.write(tdata)

        else:  # pyexiv2-0.2.0 and above
            try:
                previews = self.plugin_image.previews
                if not previews:
                    print(_('Error: %s does not contain an EXIF thumbnail.') % filename)
                    self.close_window(self.tbarea)

                # Get the largest preview available...
                preview = previews[-1]
                width, height = preview.dimensions
            except (IOError, OSError):
                print(_('Error: %s does not contain an EXIF thumbnail.') % filename)
                self.close_window(self.tbarea)

            # Create a GTK pixbuf loader to read the thumbnail data
            pbloader = gtk.gdk.PixbufLoader()
            pbloader.write(preview.data)

        return pbloader, width, height

    def build_thumbnail_gui(self, pbloader, width, height):
        """
        builds the thumbnail viewing area.
        """

        main_vbox = gtk.VBox()
        main_vbox.set_size_request((width - 30), (height - 30))

        hbox = gtk.HBox(False, 0)
        main_vbox.pack_start(hbox, expand =False, fill =False, padding =5)
        hbox.show()

        # Get the resulting pixbuf and build an image to be displayed...
        pixbuf = pbloader.get_pixbuf()
        pbloader.close()

        imgwidget = gtk.Image()
        imgwidget.set_from_pixbuf(pixbuf)
        hbox.pack_start(imgwidget, expand = False, fill =True, padding =0)
        imgwidget.show()

        main_vbox.show_all()
        return main_vbox

    def __convert_dialog(self, object):
        """
        Handles the Convert question Dialog...
        """

        # Convert and delete original file or just convert...
        OptionDialog(_("Edit Image Exif Metadata"), _("WARNING: You are about to convert this "
            "image into a .jpeg image.  Are you sure that you want to do this?"), 
            _("Convert and Delete"), self.__convert_delete, _("Convert"), self.__convert_only)

    def __convert_copy(self, full_path =None):
        """
        Will attempt to convert an image to jpeg if it is not?
        """

        if full_path is None:
            full_path = self.image_path

        # get image filepath and its filename...
        filepath, basename = os.path.split(self.basename)
        
        # get extension selected for converting this image...
        ext_type = self.exif_widgets["ImageTypes"].get_active()
        if ext_type >= 1:
            basename += self._VCONVERTMAP[ext_type]

            # new file name and dirpath...
            dest_file = os.path.join(filepath, basename)

            # open source image file...
            im = Image.open(full_path)
            im.save(dest_file) 

            # pyexiv2 source image file...
            if OLD_API:  # prior to pyexiv2-0.2.0...
                src_meta = pyexiv2.Image(full_path)
                src_meta.readMetadata()
            else:
                src_meta = pyexiv2.ImageMetadata(full_path)
                src_meta.read()

            # check to see if source image file has any Exif metadata?
            if _get_exif_keypairs(src_meta):

                if OLD_API:  # prior to pyexiv2-0.2.0
                    # Identify the destination image file...
                    dest_meta = pyexiv2.Image(dest_file)
                    dest_meta.readMetadata()

                    # copy source metadata to destination file... 
                    src_meta.copy(dest_meta, comment =False)
                    dest_meta.writeMetadata()
                else:  # pyexiv2-0.2.0 and above...
                    # Identify the destination image file...
                    dest_meta = pyexiv2.ImageMetadata(dest_file)
                    dest_meta.read()

                    # copy source metadata to destination file... 
                    src_meta.copy(dest_meta, comment =False)
                    dest_meta.write()

            return dest_file
        else:
            return False

    def __convert_delete(self, full_path =None):
        """
        will convert an image file and delete original non-jpeg image.
        """

        if full_path is None:
            full_path = self.image_path

        # Convert image and copy over it's Exif metadata (if any?)
        newfilepath = self.__convert_copy(full_path)
        if newfilepath:

            # delete original file from this computer and set new filepath...
            try:
                os.remove(full_path)
                delete_results = True
            except (IOError, OSError):
                delete_results = False
            if delete_results:

                # check for new destination and if source image file is removed?
                if (os.path.isfile(newfilepath) and not os.path.isfile(full_path) ):
                    self.__update_media_path(newfilepath)

                    # notify user about the convert, delete, and new filepath...
                    self.exif_widgets["MessageArea"].set_text(_("Your image has been "
                        "converted and the original file has been deleted, and "
                        "the full path has been updated!"))
                else:
                    self.exif_widgets["MessageArea"].set_text(_("There has been an error, "
                        "Please check your source and destination file paths..."))
        else:
            self.exif_widgets["MessageArea"].set_text(_("There was an error in "
                "deleting the original file.  You will need to delete it yourself!"))

    def __convert_only(self, full_path =None):
        """
        This will only convert the file and update the media object path.
        """

        if full_path is None:
            full_path = self.image_path

        # the convert was sucessful, then update media path?
        newfilepath = self.__convert_copy(full_path)
        if newfilepath:

            # update the media object path...
            self.__update_media_path(newfilepath)
        else:
            self.exif_widgets["MessageArea"].set_text(_("There was an error "
                "in converting your image file."))

    def __update_media_path(self, newfilepath =None):
        """
        update the media object's media path.
        """

        if newfilepath:
            db = self.dbstate.db

            # begin database tranaction to save media object new path...
            with DbTxn(_("Media Path Update"), db) as trans:
                self.orig_image.set_path(newfilepath)

                db.commit_media_object(self.orig_image, trans)
                db.request_rebuild()
        else:
            self.exif_widgets["MessageArea"].set_text(_("There has been an "
                "error in updating the image file's path!"))

    def __help_page(self, addonwiki =None):
        """
        will bring up a Wiki help page.
        """

        addonwiki = 'Edit Image Exif Metadata' 
        GrampsDisplay.help(webpage =addonwiki)

    def activate_buttons(self, buttonlist):
        """
        Enable/ activate the buttons that are in buttonlist
        """

        for widget in buttonlist:
            self.exif_widgets[widget].set_sensitive(True)

    def deactivate_buttons(self, buttonlist):
        """
        disable/ de-activate buttons in buttonlist

        *** if All, then disable ALL buttons in the current display...
        """

        if buttonlist == ["All"]:
            buttonlist = [(buttonname) for buttonname in _BUTTONTIPS.keys()
                    if buttonname is not "Help"]

        for widget in buttonlist:
            self.exif_widgets[widget].set_sensitive(False)

    def active_buttons(self, obj):
        """
        will handle the toggle action of the Edit button.

        If there is no Exif metadata, then the data fields are connected to the 
        'changed' signal to be able to activate the Edit button once data has been entered
        into the data fields...

        Activate these buttons once info has been entered into the data fields...
        """

        if not self.exif_widgets["Edit"].get_sensitive():
            self.activate_buttons(["Edit"])

            # set Message Area to Entering Data...
            self.exif_widgets["MessageArea"].set_text(_("Entering data..."))

        if EXIV2_FOUND:
            if not self.exif_widgets["Delete"].get_sensitive():
                self.activate_buttons(["Delete"])

        # if Save is in the list of button tooltips, then check it too?
        if "Save" in _BUTTONTIPS.keys():
            if not self.exif_widgets["Save"].get_sensitive():
                self.activate_buttons(["Save"])  

    def display_edit(self, object):
        """
        creates the editing area fields.
        """

        tip = _("Click the close button when you are finished modifying this "
                "image's Exif metadata.")

        self.edtarea = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.edtarea.tooltip = tip
        self.edtarea.set_title( self.orig_image.get_description() )
        self.edtarea.set_default_size(525, 560)
        self.edtarea.set_border_width(10)
        self.edtarea.connect("destroy", lambda w: self.edtarea.destroy() )

        # create a new scrolled window.
        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_border_width(10)
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.edtarea.add(scrollwindow)
        scrollwindow.show()

        vbox = self.__build_edit_gui()
        scrollwindow.add_with_viewport(vbox)
        self.edtarea.show()

        # display all fields and button tooltips...
        # need to add Save and Close over here...
        _BUTTONTIPS.update( (key, tip) for key, tip in {

            # Add the Save button...
            "Save" : _("Saves a copy of the data fields into the image's Exif metadata."),

            # Add the Close button...
            "Close" : _("Closes this popup Edit window.\n"
                "WARNING: This action will NOT Save any changes/ modification made to this "
                "image's Exif metadata."),

            # Clear button...
            "Clear" : _("This button will clear all of the data fields shown here."),

            # Re- display the data fields button...
            "Copy" : _("Re -display the data fields that were cleared from the Edit Area.") }.items() )

        # True, True -- all data fields and button tooltips will be displayed...
        self._setup_widget_tips(fields =True, buttons = True)
 
        # display all data fields and their values...
        self.edit_area()

    def __build_edit_gui(self):
        """
        will build the edit screen ...
        """

        main_vbox = gtk.VBox()
        main_vbox.set_border_width(10)
        main_vbox.set_size_request(480, 460)

        # Notification Area for the Edit Area...
        label = self.__create_label("Edit:Message", False, width =440, height = 25)
        main_vbox.pack_start(label, expand = False, fill =True, padding =5)

        # Media Title Frame...
        title_frame = gtk.Frame(_("Media Object Title"))
        title_frame.set_size_request(470, 60)
        main_vbox.pack_start(title_frame, expand =False, fill =True, padding =10)
        title_frame.show()

        new_hbox = gtk.HBox(False, 0)
        title_frame.add(new_hbox)
        new_hbox.show()

        event_box = gtk.EventBox()
        event_box.set_size_request(440, 40)
        new_hbox.pack_start(event_box, expand =False, fill =True, padding =10)
        event_box.show()

        entry = gtk.Entry(max =100)
        event_box.add(entry)
        self.exif_widgets["MediaTitle"] = entry
        entry.show()

        # create the data fields...
        # ***Description, Artist, and Copyright
        gen_frame = gtk.Frame(_("General Data"))
        gen_frame.set_size_request(470, 155)
        main_vbox.pack_start(gen_frame, expand =False, fill =True, padding =10)
        gen_frame.show()

        new_vbox = gtk.VBox(False, 0)
        gen_frame.add(new_vbox)
        new_vbox.show()

        for widget, text in [
            ("Description", _("Description :") ),
            ("Artist",      _("Artist :") ),
            ("Copyright",   _("Copyright :") ) ]:
 
            new_hbox = gtk.HBox(False, 0)
            new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =5)
            new_hbox.show()

            label = self.__create_label(False, text, width =90, height =25)
            new_hbox.pack_start(label, expand =False, fill =False, padding =0)

            event_box = gtk.EventBox()
            event_box.set_size_request(360, 30)
            new_hbox.pack_start(event_box, expand =False, fill =False, padding =0)
            event_box.show()

            entry = gtk.Entry(max =100)
            event_box.add(entry)
            self.exif_widgets[widget] = entry
            entry.show()

        # iso format: Year, Month, Day spinners...
        datetime_frame = gtk.Frame(_("Date/ Time"))
        datetime_frame.set_size_request(470, 90)
        main_vbox.pack_start(datetime_frame, expand =False, fill =False, padding =0)
        datetime_frame.show()

        new_vbox = gtk.VBox(False, 0)
        new_vbox.set_border_width(5)
        datetime_frame.add(new_vbox)
        new_vbox.show()

        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =0)
        new_hbox.show()

        for widget, text in [
            ("Original",     _("Original Date/ Time :") ),
            ("Modified",     _("Last Changed :") ) ]:

            vbox2 = gtk.VBox(False, 0)
            new_hbox.pack_start(vbox2, expand =False, fill =False, padding =5)
            vbox2.show()

            label = self.__create_label(widget, text, width =150, height =25)
            vbox2.pack_start(label, expand =False, fill =False, padding =0)
            label.show()

            event_box = gtk.EventBox()
            event_box.set_size_request(215, 30)
            vbox2.pack_start(event_box, expand =False, fill =False, padding =0)
            event_box.show()

            entry = ValidatableMaskedEntry()
            entry.connect('validate', self.validate_datetime, widget)
            event_box.add(entry)
            self.exif_widgets[widget] = entry
            entry.show()

            self.dates[widget] = None

        # GPS coordinates...
        latlong_frame = gtk.Frame(_("Latitude/ Longitude/ Altitude GPS coordinates"))
        latlong_frame.set_size_request(470, 80)
        main_vbox.pack_start(latlong_frame, expand =False, fill =False, padding =0)
        latlong_frame.show()

        new_vbox = gtk.VBox(False, 0)
        latlong_frame.add(new_vbox)
        new_vbox.show()

        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =0)
        new_hbox.show()

        for widget, text in [
            ("Latitude",  _("Latitude :") ),
            ("Longitude", _("Longitude :") ),
            ("Altitude",  _("Altitude :") ) ]:

            vbox2 = gtk.VBox(False, 0)
            new_hbox.pack_start(vbox2, expand =False, fill =False, padding =5)
            vbox2.show()

            label = self.__create_label(widget, text, width =90, height =25)
            vbox2.pack_start(label, expand =False, fill =False, padding =0)
            label.show()

            event_box = gtk.EventBox()
            event_box.set_size_request(141, 30)
            vbox2.pack_start(event_box, expand =False, fill =False, padding =0)
            event_box.show()

            entry = ValidatableMaskedEntry()
            entry.connect('validate', self.validate_coordinate, widget)
            event_box.add(entry)
            self.exif_widgets[widget] = entry
            entry.show()

        # Help, Save, Clear, Copy, and Close buttons...
        new_hbox = gtk.HBox(False, 0)
        main_vbox.pack_start(new_hbox, expand =False, fill =True, padding =5)
        new_hbox.show()

        for (widget, text, callback, icon, is_sensitive) in [
            ("Help",  False, [self.__help_page],                 gtk.STOCK_HELP, True),
            ("Save",  False, [self.save_metadata,
                             self.__display_exif_tags,
                             self.update],                       gtk.STOCK_SAVE, True), 
            ("Clear", False, [self.clear_metadata],              gtk.STOCK_CLEAR, True),
            ("Copy",  False, [self.__display_exif_tags],         gtk.STOCK_COPY, True),
            ("Close", False, [lambda w: self.edtarea.destroy()], gtk.STOCK_CLOSE, True) ]:

            event_box = gtk.EventBox()
            event_box.set_size_request(81, 30)
            new_hbox.pack_start(event_box, expand =False, fill =True, padding =5)
            event_box.show()

            event_box.add( self.__create_button(
                widget, text, callback, icon, is_sensitive) )

        main_vbox.show_all()
        return main_vbox

    def set_datetime(self, widget, field):
        """
        Parse date and time from text entry
        """
        value = _parse_datetime(unicode(widget.get_text()))
        if value is not None:
            self.dates[field] = "%04d:%02d:%02d %02d:%02d:%02d" % (
                                    value.year, value.month, value.day,
                                    value.hour, value.minute, value.second)
        else:
            self.dates[field] = None

    def validate_datetime(self, widget, data, field):
        """
        Validate current date and time in text entry
        """
        if self.dates[field] is None:
            return ValidationError(_('Bad Date/Time'))

    def validate_coordinate(self, widget, data, field):
        """
        Validate current latitude or longitude in text entry
        """
        if field == "Latitude" and not conv_lat_lon(data, "0", "ISO-D"):
            return ValidationError(_(u"Invalid latitude (syntax: 18\u00b09'") +
                                   _('48.21"S, -18.2412 or -18:9:48.21)'))
        if field == "Longitude" and not conv_lat_lon("0", data, "ISO-D"):
            return ValidationError(_(u"Invalid longitude (syntax: 18\u00b09'") +
                                   _('48.21"E, -18.2412 or -18:9:48.21)'))

    def __wipe_dialog(self, object):
        """
        Handles the Delete Dialog...
        """

        QuestionDialog(_("Edit Image Exif Metadata"), _("WARNING!  You are about to completely "
            "delete the Exif metadata from this image?"), _("Delete"),
                self.strip_metadata)

    def _get_value(self, keytag):
        """
        gets the value from the Exif Key, and returns it...

        @param: keytag -- image metadata key
        """

        if OLD_API:
            keyvalu = self.plugin_image[keytag]

        else:
            try:
                value = self.plugin_image.__getitem__(keytag)
                keyvalu = value.value

            except (KeyError, ValueError, AttributeError):
                keyvalu = False

        return keyvalu

    def clear_metadata(self, object):
        """
        clears all data fields to nothing
        """

        for widget in _TOOLTIPS.keys():
            self.exif_widgets[widget].set_text("")

    def edit_area(self, mediadatatags =None):
        """
        displays the image Exif metadata in the Edit Area...
        """
        if mediadatatags is None:
            mediadatatags = _get_exif_keypairs(self.plugin_image)
        mediadatatags = [keytag for keytag in mediadatatags if keytag in _DATAMAP]

        for keytag in mediadatatags:
            widget = _DATAMAP[keytag]

            tag_value = self._get_value(keytag)
            if tag_value:

                if widget in ["Description", "Artist", "Copyright"]:
                    self.exif_widgets[widget].set_text(tag_value)

                # Last Changed/ Modified...
                elif widget in ["Modified", "Original"]:
                    use_date = format_datetime(tag_value)
                    if use_date:
                        self.exif_widgets[widget].set_text(use_date)

                    # set Modified Datetime to non-editable... 
                    if (widget == "Modified" and use_date):
                        self.exif_widgets[widget].set_editable(False)

                # LatitudeRef, Latitude, LongitudeRef, Longitude...
                elif widget == "Latitude":

                    latitude, longitude = tag_value, self._get_value(_DATAMAP["Longitude"])

                    # if latitude and longitude exist, display them?
                    if (latitude and longitude):

                        # split latitude metadata into (degrees, minutes, and seconds)
                        latdeg, latmin, latsec = rational_to_dms(latitude)

                        # split longitude metadata into degrees, minutes, and seconds
                        longdeg, longmin, longsec = rational_to_dms(longitude)

                        # check to see if we have valid GPS coordinates?
                        latfail = any(coords == False for coords in [latdeg, latmin, latsec])
                        longfail = any(coords == False for coords in [longdeg, longmin, longsec])
                        if (not latfail and not longfail):

                            # Latitude Direction Reference
                            latref = self._get_value(_DATAMAP["LatitudeRef"] )

                            # Longitude Direction Reference
                            longref = self._get_value(_DATAMAP["LongitudeRef"] )

                            # set display for Latitude GPS coordinates
                            latitude = """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, latref)
                            self.exif_widgets["Latitude"].set_text(latitude)

                            # set display for Longitude GPS coordinates
                            longitude = """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, longref)
                            self.exif_widgets["Longitude"].set_text(longitude)

                            self.exif_widgets["Latitude"].validate()
                            self.exif_widgets["Longitude"].validate()

                elif widget == "Altitude":
                    altitude = tag_value
                    altref = self._get_value(_DATAMAP["AltitudeRef"])
 
                    if (altitude and altref):
                        altitude = convert_value(altitude)
                        if altitude:
                            if altref == "1":
                                altitude = "-" + altitude
                            self.exif_widgets[widget].set_text(altitude)

        # Media Object Title...
        self.media_title = self.orig_image.get_description()
        self.exif_widgets["MediaTitle"].set_text(self.media_title)

    def _set_value(self, keytag, keyvalu):
        """
        sets the value for the metadata keytags
        """

        if OLD_API:
            self.plugin_image[keytag] = keyvalu

        else:
            try:
                self.plugin_image.__setitem__(keytag, keyvalu)
            except KeyError:
                self.plugin_image[keytag] = pyexiv2.ExifTag(keytag, keyvalu)
            except (ValueError, AttributeError):
                pass

    def write_metadata(self, plugininstance):
        """
        writes the Exif metadata to the image.

        OLD_API -- prior to pyexiv2-0.2.0
                      -- pyexiv2-0.2.0 and above... 
        """
        if OLD_API:
            plugininstance.writeMetadata()

        else:
            plugininstance.write()

    def close_window(self, widgetWindow):
        """
        closes the window title by widgetWindow.
        """

        lambda w: widgetWindow.destroy()

    def convert_format(self, latitude, longitude, format):
        """
        Convert GPS coordinates into a specified format.
        """

        if (not latitude and not longitude):
            return [False]*2

        latitude, longitude = conv_lat_lon(  unicode(latitude),
                                            unicode(longitude),
                                            format)
        return latitude, longitude

    def convert2dms(self, latitude =None, longitude =None):
        """
        will convert a decimal GPS coordinates into degrees, minutes, seconds
        for display only
        """

        if (not latitude and not longitude):
            return [False]*2

        latitude, longitude = self.convert_format(latitude, longitude, "DEG-:")

        return latitude, longitude

    def save_metadata(self, mediadatatags =None):
        """
        gets the information from the plugin data fields
        and sets the keytag = keyvalue image metadata
        """
        db = self.dbstate.db

        # get a copy of all the widgets and their current values...
        mediadatatags = list( (widget, self.exif_widgets[widget].get_text() )
                for widget in _TOOLTIPS.keys() )
        mediadatatags.sort()
        for widgetname, widgetvalu in mediadatatags:

            # Description, Artist, Copyright...
            if widgetname in ["Description", "Artist", "Copyright"]:
                self._set_value(_DATAMAP[widgetname], widgetvalu)

            # Update dynamically updated Modified field...
            elif widgetname == "Modified":
                modified = datetime.datetime.now()
                self.exif_widgets[widgetname].set_text(format_datetime(modified) )
                self.set_datetime(self.exif_widgets[widgetname], widgetname)
                if self.dates[widgetname] is not None:
                    self._set_value(_DATAMAP[widgetname], self.dates[widgetname] )
                else:
                    self._set_value(_DATAMAP[widgetname], widgetvalu)

            # Original Date/ Time...
            elif widgetname == "Original":
                if widgetvalu == '':
                    self._set_value(_DATAMAP[widgetname], widgetvalu)
                else:
                    self.set_datetime(self.exif_widgets[widgetname], widgetname)
                    if self.dates[widgetname] is not None:

                        # modify the media object date if it is not already set?
                        mediaobj_date = self.orig_image.get_date_object()
                        if mediaobj_date.is_empty():
                            objdate_ = Date()
                            widgetvalu = _parse_datetime(widgetvalu) 
                            try:
                                objdate_.set_yr_mon_day(widgetvalu.year,
                                                       widgetvalu.month,
                                                       widgetvalu.day)
                                gooddate = True
                            except ValueError:
                                gooddate = False
                            if gooddate:

                                # begin database tranaction to save media object's date...
                                with DbTxn(_("Create Date Object"), db) as trans:
                                    self.orig_image.set_date_object(objdate_)
                                    db.commit_media_object(self.orig_image, trans)
                                    db.request_rebuild()

            # Latitude/ Longitude...
            elif widgetname == "Latitude":
                latitude  =  self.exif_widgets["Latitude"].get_text()
                longitude = self.exif_widgets["Longitude"].get_text()
                if (latitude and longitude):
                    if (latitude.count(" ") == longitude.count(" ") == 0):
                        latitude, longitude = self.convert2dms(latitude, longitude)

                    # remove symbols before saving...
                    latitude, longitude = _removesymbolsb4saving(latitude, longitude)

                    # split Latitude/ Longitude into its (d, m, s, dir)...
                    latitude  =  coordinate_splitup(latitude)
                    longitude = coordinate_splitup(longitude)

                    if "N" in latitude:
                        latref = "N"
                    elif "S" in latitude:
                        latref = "S"
                    elif "-" in latitude:
                        latref = "-"
                    latitude.remove(latref)

                    if latref == "-": latref = "S"

                    if "E" in longitude:
                        longref = "E"
                    elif "W" in longitude:
                        longref = "W"
                    elif "-" in longitude:
                        longref = "-"
                    longitude.remove(longref)

                    if longref == "-": longref = "W"

                    # convert Latitude/ Longitude into pyexiv2.Rational()...
                    latitude  =  coords_to_rational(latitude)
                    longitude = coords_to_rational(longitude)

                    # save LatitudeRef/ Latitude... 
                    self._set_value(_DATAMAP["LatitudeRef"], latref)
                    self._set_value(_DATAMAP["Latitude"], latitude)

                    # save LongitudeRef/ Longitude...
                    self._set_value(_DATAMAP["LongitudeRef"], longref)
                    self._set_value(_DATAMAP["Longitude"], longitude) 

            # Altitude, and Altitude Reference...
            elif widgetname == "Altitude":
                if widgetvalu:
                    if "-" in widgetvalu:
                        widgetvalu= widgetvalu.replace("-", "")
                        altituderef = "1"
                    else:
                        altituderef = "0"

                    # convert altitude to pyexiv2.Rational for saving... 
                    widgetvalu = coords_to_rational(widgetvalu)
                else:
                    altituderef = ''

                self._set_value(_DATAMAP["AltitudeRef"], altituderef)
                self._set_value(_DATAMAP[widgetname], widgetvalu)

        # Media Title Changed or not?
        mediatitle = self.exif_widgets["MediaTitle"].get_text()
        if (self.media_title and self.media_title is not mediatitle):
            with DbTxn(_("Media Title Update"), db) as trans:
                self.orig_image.set_description(mediatitle)

                db.commit_media_object(self.orig_image, trans)
                db.request_rebuild()

        # writes all Exif Metadata to image even if the fields are all empty so as to remove the value...
        self.write_metadata(self.plugin_image)

        if mediadatatags:
            # set Message Area to Saved...
            self.exif_widgets["Edit:Message"].set_text(_("Saving Exif metadata to this image..."))
        else:
            # set Edit Message to Cleared...
            self.exif_widgets["Edit:Message"].set_text(_("All Exif metadata has been cleared..."))

    def strip_metadata(self, mediadatatags =None):
        """
        Will completely and irrevocably erase all Exif metadata from this image.
        """

        # make sure the image has Exif metadata...
        mediadatatags = _get_exif_keypairs(self.plugin_image)
        if mediadatatags:

            if EXIV2_FOUND:  # use exiv2 to delete the Exif metadata...
                try:
                    erase = subprocess.check_call( [EXIV2_FOUND, "delete", self.image_path] )
                    erase_results = str(erase) 
                except subprocess.CalledProcessError:
                    erase_results = False

            else:  # use pyexiv2 to delete Exif metadata...
                for keytag in mediadatatags:
                    del self.plugin_image[keytag]
                erase_results = True

            if erase_results:
                # write wiped metadata to image...
                self.write_metadata(self.plugin_image)

                for widget in ["MediaLabel", "MimeType", "ImageSize", "MessageArea", "Total"]:
                    self.exif_widgets[widget].set_text("") 

                self.exif_widgets["MessageArea"].set_text(_("All Exif metadata "
                    "has been deleted from this image..."))
                self.update()

            else:
                self.exif_widgets["MessageArea"].set_text(_("There was an error "
                    "in stripping the Exif metadata from this image..."))

def _removesymbolsb4saving(latitude, longitude):
    """
    will recieve a DMS with symbols and return it without them

    @param: latitude  --  Latitude GPS coordinates
    @param: longitude -- GPS Longitude coordinates
    """

    # check to see if latitude/ longitude exist?
    if (latitude and longitude):

        # remove degrees, minutes, seconds symbols if they exist in 
        # Latitude/ Longitude...
        for symbol in ["°", "#", "먊", "′", "'", '″', '"']:

            if symbol in latitude:
                latitude = latitude.replace(symbol, "")

            if symbol in longitude:
                longitude = longitude.replace(symbol, "")

    return latitude, longitude

def string_to_rational(coordinate):
    """
    convert string to rational variable for GPS
    """

    if coordinate:

        if '.' in coordinate:
            value1, value2 = coordinate.split('.')
            return pyexiv2.Rational(int(float(value1 + value2)), 10**len(value2))
        else:
            return pyexiv2.Rational(int(coordinate), 1)

def coordinate_splitup(coordinates):
    """
    will split up the coordinates into a list
    """

    # Latitude, Longitude...
    if (":" in coordinates and coordinates.find(" ") == -1):
        return [(coordinate) for coordinate in coordinates.split(":")]

    elif (" " in coordinates and coordinates.find(":") == -1):
        return [(coordinate) for coordinate in coordinates.split(" ")]

    return None

def coords_to_rational(coordinates):
    """
    returns the rational equivalent for (degrees, minutes, seconds)...
    """

    return [string_to_rational(coordinate) for coordinate in coordinates]

def convert_value(value):
    """
    will take a value from the coordinates and return its value
    """

    if isinstance(value, (Fraction, pyexiv2.Rational)):
        return str((Decimal(value.numerator) / Decimal(value.denominator)))

    return value

def rational_to_dms(coordinates):
    """
    takes a rational set of coordinates and returns (degrees, minutes, seconds)

    [Fraction(40, 1), Fraction(0, 1), Fraction(1079, 20)]
    """

    # coordinates look like:
    #     [Rational(38, 1), Rational(38, 1), Rational(150, 50)]
    # or [Fraction(38, 1), Fraction(38, 1), Fraction(318, 100)]   
    return [convert_value(coordinate) for coordinate in coordinates]

def _get_exif_keypairs(plugin_image):
    """
    Will be used to retrieve and update the Exif metadata from the image.
    """

    if plugin_image:
        return [keytag for keytag in (plugin_image.exifKeys() if OLD_API
                else plugin_image.exif_keys) ]
    else:
        return False
