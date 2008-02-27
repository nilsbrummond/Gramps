#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008 Lukasz Rymarczyk
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
import sys

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import PluginUtils
import Utils
import BaseDoc
from ReportBase import CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_BOOK, \
    CATEGORY_GRAPHVIZ
from _PaperMenu import paper_sizes
import os
import const

#------------------------------------------------------------------------
#
# Private Functions
#
#------------------------------------------------------------------------
def _initialize_options(options, dbase):
    """
    Validates all options by making sure that their values are consistent with
    the database.
    
    menu: The Menu class
    dbase: the database the options will be applied to
    """
    if not hasattr(options, "menu"):
        return
    menu = options.menu
    
    for name in menu.get_all_option_names():
        option = menu.get_option_by_name(name)

        if isinstance(option, PluginUtils.PersonOption):
            pid = option.get_value()
            person = dbase.get_person_from_gramps_id(pid)
            if not person:
                person = dbase.get_default_person()
                option.set_value(person.get_gramps_id())
                if not person:
                    print "Please specify a person"
                    sys.exit(0)
        
        elif isinstance(option, PluginUtils.FamilyOption):
            fid = option.get_value()
            family = dbase.get_family_from_gramps_id(fid)
            if not family:
                person = dbase.get_default_person()
                family_list = person.get_family_handle_list()
                if family_list:
                    family_handle = family_list[0]
                else:
                    family_handle = dbase.get_family_handles()[0]
                family = dbase.get_family_from_handle(family_handle)
                option.set_value(family.get_gramps_id())

#------------------------------------------------------------------------
#
# Command-line report
#
#------------------------------------------------------------------------
class CommandLineReport:
    """
    Provide a way to generate report from the command line.
    """

    def __init__(self,database, name,category, option_class, options_str_dict,
                 noopt=False):
        self.database = database
        self.category = category
        self.format = None
        self.option_class = option_class(name, database)
        self.option_class.load_previous_values()
        _initialize_options(self.option_class, database)
        self.show = options_str_dict.pop('show', None)
        self.options_str_dict = options_str_dict
        self.init_options(noopt)
        self.parse_option_str()
        self.show_options()

    def init_options(self, noopt):
        self.options_dict = {
            'of'        : self.option_class.handler.module_name,
            'off'       : self.option_class.handler.get_format_name(),
            'style'     : \
                    self.option_class.handler.get_default_stylesheet_name(),
            'papers'    : self.option_class.handler.get_paper_name(),
            'papero'    : self.option_class.handler.get_orientation(),
            'template'  : self.option_class.handler.get_template_name(),
            }

        self.options_help = {
            'of'        : ["=filename","Output file name. MANDATORY"],
            'off'       : ["=format","Output file format."],
            'style'     : ["=name","Style name."],
            'papers'    : ["=name","Paper size name."],
            'papero'    : ["=num","Paper orientation number."],
            'template'  : ["=name","Template name (HTML only)."],
            }

        if noopt:
            return

        # Add report-specific options
        for key in self.option_class.handler.options_dict.keys():
            if key not in self.options_dict.keys():
                self.options_dict[key] = \
                                   self.option_class.handler.options_dict[key]

        # Add help for report-specific options
        for key in self.option_class.options_help.keys():
            if key not in self.options_help.keys():
                self.options_help[key] = self.option_class.options_help[key]

    def parse_option_str(self):
        for opt in self.options_str_dict.keys():
            if opt in self.options_dict.keys():
                converter = Utils.get_type_converter(self.options_dict[opt])
                self.options_dict[opt] = converter(self.options_str_dict[opt])
                self.option_class.handler.options_dict[opt] = \
                                                        self.options_dict[opt]
            else:
                print "Ignoring unknown option: %s" % opt

        self.option_class.handler.output = self.options_dict['of']
        self.options_help['of'].append(os.path.join(const.USER_HOME,
                                                    "whatever_name"))

        if self.category == CATEGORY_TEXT:
            for item in PluginUtils.textdoc_list:
                if item[7] == self.options_dict['off']:
                    self.format = item[1]
            if self.format is None:
                # Pick the first one as the default.
                self.format = PluginUtils.textdoc_list[0][1]
            self.options_help['off'].append(
                [ item[7] for item in PluginUtils.textdoc_list ]
            )
            self.options_help['off'].append(False)
        elif self.category == CATEGORY_DRAW:
            for item in PluginUtils.drawdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            if self.format is None:
                # Pick the first one as the default.
                self.format = PluginUtils.drawdoc_list[0][1]
            self.options_help['off'].append(
                [ item[6] for item in PluginUtils.drawdoc_list ]
            )
            self.options_help['off'].append(False)
        elif self.category == CATEGORY_BOOK:
            for item in PluginUtils.bookdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            if self.format is None:
                # Pick the first one as the default.
                self.format = PluginUtils.bookdoc_list[0][1]
            self.options_help['off'].append(
                [ item[6] for item in PluginUtils.bookdoc_list ]
            )
            self.options_help['off'].append(False)
        else:
            self.format = None

        for paper in paper_sizes:
            if paper.get_name() == self.options_dict['papers']:
                self.paper = paper
        self.option_class.handler.set_paper(self.paper)
        self.options_help['papers'].append(
            [ paper.get_name() for paper in paper_sizes 
                        if paper.get_name() != _("Custom Size") ] )
        self.options_help['papers'].append(False)

        self.orien = self.options_dict['papero']
        self.options_help['papero'].append([
            "%d\tPortrait" % BaseDoc.PAPER_PORTRAIT,
            "%d\tLandscape" % BaseDoc.PAPER_LANDSCAPE ] )
        self.options_help['papero'].append(False)

        self.template_name = self.options_dict['template']
        self.options_help['template'].append(os.path.join(const.USER_HOME,
                                                          "whatever_name"))

        if self.category in (CATEGORY_TEXT,CATEGORY_DRAW):
            default_style = BaseDoc.StyleSheet()
            self.option_class.make_default_style(default_style)

            # Read all style sheets available for this item
            style_file = self.option_class.handler.get_stylesheet_savefile()
            self.style_list = BaseDoc.StyleSheetList(style_file,default_style)

            # Get the selected stylesheet
            style_name =self.option_class.handler.get_default_stylesheet_name()
            self.selected_style = self.style_list.get_style_sheet(style_name)
            
            self.options_help['style'].append(
                self.style_list.get_style_names() )
            self.options_help['style'].append(False)

    def show_options(self):
        """
        Print available options on the CLI.
        """
        if not self.show:
            return
        elif self.show == 'all':
            print "   Available options:"
            for key in self.options_dict.keys():
                if key in self.options_dict.keys():
                # Make the output nicer to read, assume that tab has 8 spaces
                    if len(key) < 10:
                        print "      %s\t\t%s (%s)" % (key, 
                                                    self.options_help[key][1], 
                                                    self.options_help[key][0])
                    else:
                        print "      %s\t%s (%s)" % (key, 
                                                     self.options_help[key][1], 
                                                     self.options_help[key][0])
                else:
                    print " %s" % key
            print "   Use 'show=option' to see description and acceptable values"
        elif self.show in self.options_dict.keys():
            print '   %s%s\t%s' % (self.show,
                                    self.options_help[self.show][0],
                                    self.options_help[self.show][1])
            print "   Available values are:"
            vals = self.options_help[self.show][2]
            if type(vals) in [list,tuple]:
                if self.options_help[self.show][3]:
                    for num in range(len(vals)):
                        print "      %d\t%s" % (num,vals[num])
                else:
                    for val in vals:
                        print "      %s" % val
            else:
                print "      %s" % self.options_help[self.show][2]

        else:
            self.show = None

#------------------------------------------------------------------------
#
# Command-line report generic task
#
#------------------------------------------------------------------------
def cl_report(database, name, category, report_class, options_class, 
              options_str_dict):
    
    clr = CommandLineReport(database, name, category, options_class, 
                            options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    # write report
    try:
        if category in [CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_BOOK, \
                        CATEGORY_GRAPHVIZ]:
            clr.option_class.handler.doc = clr.format(
                        clr.selected_style,
                        BaseDoc.PaperStyle(clr.paper,clr.orien),
                        clr.template_name)
        MyReport = report_class(database, clr.option_class)
        MyReport.doc.init()
        MyReport.begin_report()
        MyReport.write_report()
        MyReport.end_report()
    except:
        log.error("Failed to write report.", exc_info=True)
