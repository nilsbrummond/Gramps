#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Brian G. Matherly
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
# $Id: _MenuOptions.py 9422 2007-11-28 22:21:18Z dsblank $

"""
Abstracted option handling.
"""
#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import _Tool as Tool

#-------------------------------------------------------------------------
#
# Option class
#
#-------------------------------------------------------------------------
class Option:
    """
    This class serves as a base class for all options. All Options must 
    minimally provide the services provided by this class. Options are allowed 
    to add additional functionality.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @param value: An initial value for this option.
            Example: True
        @type value: The type will depend on the type of option.
        @return: nothing
        """
        self.__value = value
        self.__label = label
        self.__help_str = ""
        
    def get_label(self):
        """
        Get the friendly label for this option.
        
        @return: string
        """
        return self.__label
    
    def set_label(self,label):
        """
        Set the friendly label for this option.
        
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @return: nothing
        """
        self.__label = label
        
    def get_value(self):
        """
        Get the value of this option.
        
        @return: The option value.
        """
        return self.__value
    
    def set_value(self,value):
        """
        Set the value of this option.
        
        @param value: A value for this option.
            Example: True
        @type value: The type will depend on the type of option.
        @return: nothing
        """
        self.__value = value
        
    def get_help(self):
        """
        Get the help information for this option.
        
        @return: A string that provides additional help beyond the label.
        """
        return self.__help_str
        
    def set_help(self,help):
        """
        Set the help information for this option.
        
        @param help: A string that provides additional help beyond the label.
            Example: "Whether to include or exclude people who are calculated 
            to be alive at the time of the generation of this report"
        @type value: string
        @return: nothing
        """
        self.__help_str = help

    def add_dialog_category(self, dialog, category):
        """
        Add the GUI object to the dialog on the appropriate tab.
        """
        dialog.add_frame_option(category, self.get_label(), self.gobj)

    def add_tooltip(self, tooltip):
        """
        Add the option's help to the GUI object.
        """
        tooltip.set_tip(self.gobj, self.get_help())
        
        
#-------------------------------------------------------------------------
#
# StringOption class
#
#-------------------------------------------------------------------------
class StringOption(Option):
    """
    This class describes an option that is a simple one-line string.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Page header"
        @type label: string
        @param value: An initial value for this option.
            Example: "Generated by GRAMPS"
        @type value: string
        @return: nothing
        """
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a StringOption (single line text) to the dialog.
        """
        value = self.get_value()
        self.gobj = gtk.Entry()
        self.gobj.set_text(value)

    def parse(self):
        """
        Parse the string option (single line text).
        """
        return self.gobj.get_text()
        
#-------------------------------------------------------------------------
#
# NumberOption class
#
#-------------------------------------------------------------------------
class NumberOption(Option):
    """
    This class describes an option that is a simple number with defined maximum 
    and minimum values.
    """
    def __init__(self,label,value,min,max):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Number of generations to include"
        @type label: string
        @param value: An initial value for this option.
            Example: 5
        @type value: int
        @param min: The minimum value for this option.
            Example: 1
        @type min: int
        @param max: The maximum value for this option.
            Example: 10
        @type value: int
        @return: nothing
        """
        Option.__init__(self,label,value)
        self.__min = min
        self.__max = max
    
    def get_min(self):
        """
        Get the minimum value for this option.
        
        @return: an int that represents the minimum value for this option.
        """
        return self.__min
    
    def get_max(self):
        """
        Get the maximum value for this option.
        
        @return: an int that represents the maximum value for this option.
        """
        return self.__max

    def make_gui_obj(self, gtk, dialog):
        """
        Add a NumberOption to the dialog.
        """
        value = self.get_value()
        adj = gtk.Adjustment(1,self.get_min(),self.get_max(),1)
        self.gobj = gtk.SpinButton(adj)
        self.gobj.set_value(value)

    def parse(self):
        """
        Parse the object and return.
        """
        return int(self.gobj.get_value_as_int())
                

#-------------------------------------------------------------------------
#
# TextOption class
#
#-------------------------------------------------------------------------
class TextOption(Option):
    """
    This class describes an option that is a multi-line string.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Page header"
        @type label: string
        @param value: An initial value for this option.
            Example: "Generated by GRAMPS\nCopyright 2007"
        @type value: string
        @return: nothing
        """
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a TextOption to the dialog.
        """
        value = self.get_value()
        self.gobj = gtk.TextView()
        self.gobj.get_buffer().set_text("\n".join(value))
        self.gobj.set_editable(1)
        swin = gtk.ScrolledWindow()
        swin.set_shadow_type(gtk.SHADOW_IN)
        swin.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        swin.add(self.gobj)
        # Required for tooltip
        self.gobj.add_events(gtk.gdk.ENTER_NOTIFY_MASK)
        self.gobj.add_events(gtk.gdk.LEAVE_NOTIFY_MASK)

    def parse(self):
        """
        Parse the text option (multi-line text).
        """
        b = self.gobj.get_buffer()
        text_val = unicode( b.get_text( b.get_start_iter(),
                                        b.get_end_iter(),
                                        False)             )
        return text_val.split('\n')
        
#-------------------------------------------------------------------------
#
# BooleanOption class
#
#-------------------------------------------------------------------------
class BooleanOption(Option):
    """
    This class describes an option that is a boolean (True or False).
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @param value: An initial value for this option.
            Example: True
        @type value: boolean
        @return: nothing
        """
        Option.__init__(self,label,value)

    def make_gui_obj(self, gtk, dialog):
        """
        Add a BooleanOption to the dialog.
        """
        value = self.get_value()
        self.gobj = gtk.CheckButton(self.get_label())
        self.set_label("")
        self.gobj.set_active(value)
        
    def parse(self):
        """
        Parse the object and return.
        """
        return self.gobj.get_active()
        
#-------------------------------------------------------------------------
#
# EnumeratedListOption class
#
#-------------------------------------------------------------------------
class EnumeratedListOption(Option):
    """
    This class describes an option that provides a finite number of values.
    Each possible value is assigned a value and a description.
    """
    def __init__(self,label,value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Paper Size"
        @type label: string
        @param value: An initial value for this option.
            Example: 5
        @type value: int
        @return: nothing
        """
        Option.__init__(self,label,value)
        self.__items = []
        
    def add_item(self,value,description):
        """
        Add an item to the list of possible values.
        
        @param value: The value that corresponds to this item.
            Example: 5
        @type value: int
        @param description: A description of this value.
            Example: "8.5 x 11"
        @type description: string
        @return: nothing
        """
        self.__items.append((value, description))
        
    def get_items(self):
        """
        Get all the possible values for this option.
        
        @return: an array of tuples containing (value,description) pairs.
        """
        return self.__items

    def make_gui_obj(self, gtk, dialog):
        """
        Add an EnumeratedListOption to the dialog.
        """
        v = self.get_value()
        active_index = 0
        current_index = 0 
        self.gobj = gtk.combo_box_new_text()
        for (value,description) in self.get_items():
            self.gobj.append_text(description)
            if value == v:
                active_index = current_index
            current_index += 1
        self.gobj.set_active( active_index )

    def parse(self):
        """
        Parse the EnumeratedListOption and return.
        """
        index = self.gobj.get_active()
        items = self.get_items()
        value = items[index]
        return value

#-------------------------------------------------------------------------
#
# FilterListOption class
#
#-------------------------------------------------------------------------
class FilterListOption(Option):
    """
    This class describes an option that provides a finite list of filters.
    Each possible value is assigned a type of set of filters to use.
    """
    def __init__(self,label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Filter"
        @type label: string
        @return: nothing
        """
        Option.__init__(self,label,"")
        self.__items = []
        self.__filters = []

    def add_item(self,value):
        """
        Add an item to the list of possible values.
        
        @param value: A name of a set of filters.
            Example: "person"
        @type value: string
        @return: nothing
        """
        self.__items.append(value)

    def get_items(self):
        """
        Get all the possible values for this option.
        
        @return: an array of tuples containing (value,description) pairs.
        """
        return self.__items

    def add_filter(self, filter):
        """
        Add a filter set to the list.
        
        @param filter: A filter object.
            Example: <Filter>
        @type value: Filter
        @return: nothing
        """
        self.__filters.append(filter)

    def get_filters(self):
        """
        Get all of the filter objects.
        
        @type value: Filter
        @return: an array of filter objects
        """
        return self.__filters

    def clear_filters(self):
        """
        Clear all of the filter objects.
        
        """
        self.__filters = []

    def make_gui_obj(self, gtk, dialog):
        """
        Add an FilterListOption to the dialog.
        """
        from ReportBase import ReportUtils
        self.dialog = dialog
        self.combo = gtk.combo_box_new_text()
        self.gobj = gtk.HBox()
        for filter in self.get_items():
            if filter in ["person"]:
                # FIXME: get filter list from filter sidebar?
                filter_list = ReportUtils.get_person_filters(dialog.person,
                                                             include_single=True)
                for filter in filter_list:
                    self.combo.append_text(filter.get_name())
                    self.add_filter(filter)
        # FIXME: set proper default
        self.combo.set_active(0)
        self.change_button = gtk.Button("%s..." % _('C_hange') )
        self.change_button.connect('clicked',self.on_change_clicked)
        self.gobj.pack_start(self.combo, False)
        self.gobj.pack_start(self.change_button, False)

    def on_change_clicked(self, *obj):
        from Selectors import selector_factory
        SelectPerson = selector_factory('Person')
        sel_person = SelectPerson(self.dialog.dbstate,
                                  self.dialog.uistate,
                                  self.dialog.track)
        new_person = sel_person.run()
        if new_person:
            self.dialog.person = new_person
            self.update_gui_obj()

    def update_gui_obj(self):
        # update the gui object with new filter info
        from ReportBase import ReportUtils
        for i in range(len(self.get_filters())):
            self.combo.remove_text(0)
        self.clear_filters()
        for filter in self.get_items():
            if filter in ["person"]:
                filter_list = ReportUtils.get_person_filters(self.dialog.person,
                                                             include_single=True)
                for filter in filter_list:
                    self.combo.append_text(filter.get_name())
                    self.add_filter(filter)
        # FIXME: set proper default
        self.combo.set_active(0)

    def parse(self):
        """
        Parse the object and return.
        """
        index = self.combo.get_active()
        items = self.get_filters()
        filter = items[index]
        return filter

#-------------------------------------------------------------------------
#
# Menu class
#
#-------------------------------------------------------------------------
class Menu:
    """
    Introduction
    ============
    A Menu is used to maintain a collection of options that need to be 
    represented to the user in a non-implementation specific way. The options
    can be described using the various option classes. A menu contains many
    options and associates them with a unique name and category.
    
    Usage
    =====
    Menus are used in the following way.

      1. Create a option object and configure all the attributes of the option.
      2. Add the option to the menu by specifying the option, name and category.
      3. Add as many options as necessary.
      4. When all the options are added, the menu can be stored and passed to
         the part of the system that will actually represent the menu to 
         the user.
    """
    def __init__(self):
        self.__options = {}
    
    def add_option(self,category,name,option):
        """
        Add an option to the menu.
        
        @param category: A label that describes the category that the option 
            belongs to. 
            Example: "Report Options"
        @type category: string
        @param name: A name that is unique to this option.
            Example: "generations"
        @type name: string
        @param option: The option instance to be added to this menu.
        @type option: Option
        @return: nothing
        """
        if not self.__options.has_key(category):
            self.__options[category] = []
        self.__options[category].append((name,option))
        
    def get_categories(self):
        """
        Get a list of categories in this menu.
        
        @return: a list of strings
        """
        categories = []
        for category in self.__options:
            categories.append(category)
        return categories
    
    def get_option_names(self,category):
        """
        Get a list of option names for the specified category.
        
        @return: a list of strings
        """
        names = []
        for (name,option) in self.__options[category]:
            names.append(name)
        return names
    
    def get_option(self,category,name):
        """
        Get an option with the specified category and name.
        
        @return: an Option instance or None on failure.
        """
        for (oname,option) in self.__options[category]:
            if oname == name:
                return option
        return None
    
    def get_all_option_names(self):
        """
        Get a list of all the option names in this menu.
        
        @return: a list of strings
        """
        names = []
        for category in self.__options:
            for (name,option) in self.__options[category]:
                names.append(name)
        return names
    
    def get_option_by_name(self,name):
        """
        Get an option with the specified name.
        
        @return: an Option instance or None on failure.
        """
        for category in self.__options.keys():
            for (oname,option) in self.__options[category]:
                if oname == name:
                    return option
        return None

#------------------------------------------------------------------------
#
# MenuOptions class
#
#------------------------------------------------------------------------
class MenuOptions:
    def __init__(self):
        self.menu = Menu()

    def make_default_style(self,default_style):
        pass

    def set_new_options(self):
        # Fill options_dict with report/tool defaults:
        self.options_dict = {}
        self.options_help = {}
        self.add_menu_options(self.menu)
        for name in self.menu.get_all_option_names():
            option = self.menu.get_option_by_name(name)
            self.options_dict[name] = option.get_value()
            self.options_help[name] = option.get_help()

    def add_menu_options(self,menu):
        """
        Add the user defined options to the menu.
        
        @param menu: A menu class for the options to belong to.
        @type menu: Menu
        @return: nothing
        """
        raise NotImplementedError

    def add_user_options(self, dialog):
        """
        Generic method to add user options to the gui.
        """
        import gtk
        self.tooltips = gtk.Tooltips()
        for category in self.menu.get_categories():
            for name in self.menu.get_option_names(category):
                option = self.menu.get_option(category,name)
                # override option default with xml-saved value:
                if name in self.options_dict:
                    option.set_value(self.options_dict[name])
                option.make_gui_obj(gtk, dialog)
                option.add_dialog_category(dialog, category)
                option.add_tooltip(self.tooltips)
                
    def parse_user_options(self,dialog):
        """
        Generic method to parse the user options and cache result in options_dict.
        """
        for name in self.menu.get_all_option_names():
            self.options_dict[name] = self.menu.get_option_by_name(name).parse()

    def get_option_names(self):
        """
        Return all names of options.
        """
        return self.menu.get_all_option_names()

    def get_user_value(self, name):
        """
        Get and parse the users choice.
        """
        return self.menu.get_option_by_name(name).parse()

