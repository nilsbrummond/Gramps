#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008,2011  Gary Burton
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Heinz Brinker
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

"""Place Report"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gen.ggettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from gen.plug.menu import FilterOption, PlaceListOption, EnumeratedListOption, \
                          BooleanOption
from gen.plug.report import Report
from gen.plug.report import MenuReportOptions
from gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle, TableStyle,
                            TableCellStyle, FONT_SANS_SERIF, FONT_SERIF, 
                            INDEX_TYPE_TOC, PARA_ALIGN_CENTER)
from gen.proxy import PrivateProxyDb
import DateHandler
import Sort
from gen.display.name import displayer as _nd
from gui.utils import ProgressMeter

class PlaceReport(Report):
    """
    Place Report class
    """
    def __init__(self, database, options_class):
        """
        Create the PlaceReport object produces the Place report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        places          - List of places to report on.
        center          - Center of report, person or event
        incpriv         - Whether to include private data

        """

        Report.__init__(self, database, options_class)

        menu = options_class.menu
        places = menu.get_option_by_name('places').get_value()
        self.center  = menu.get_option_by_name('center').get_value()
        self.incpriv = menu.get_option_by_name('incpriv').get_value()

        if self.incpriv:
            self.database = database
        else:
            self.database = PrivateProxyDb(database)


        filter_option = menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.sort = Sort.Sort(self.database)

        if self.filter.get_name() != '':
            # Use the selected filter to provide a list of place handles
            plist = self.database.iter_place_handles()
            self.place_handles = self.filter.apply(self.database, plist)
        else:
            # Use the place handles selected without a filter
            self.place_handles = self.__get_place_handles(places)

        self.place_handles.sort(key=self.sort.by_place_title_key)

    def write_report(self):
        """
        The routine the actually creates the report. At this point, the document
        is opened and ready for writing.
        """

        # Create progress meter bar
        self.progress = ProgressMeter(_("Place Report"), '')

        # Write the title line. Set in INDEX marker so that this section will be
        # identified as a major category if this is included in a Book report.

        title = _("Place Report")
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)        
        self.doc.start_paragraph("PLC-ReportTitle")
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()
        self.__write_all_places()

        # Close the progress meter
        self.progress.close()

    def __write_all_places(self):
        """
        This procedure writes out each of the selected places.
        """
        place_nbr = 1
        self.progress.set_pass(_("Generating report"), len(self.place_handles))
        for handle in self.place_handles:
            self.__write_place(handle, place_nbr)
            if self.center == "Event":
                self.__write_referenced_events(handle)
            elif self.center == "Person":
                self.__write_referenced_persons(handle)
            else:
              raise AttributeError("no such center: '%s'" % self.center)
            place_nbr += 1
            # increment progress bar
            self.progress.step()

    def __write_place(self, handle, place_nbr):
        """
        This procedure writes out the details of a single place
        """
        place = self.database.get_place_from_handle(handle)
        location = place.get_main_location()

        place_details = [_("Gramps ID: %s ") % place.get_gramps_id(),
                         _("Street: %s ") % location.get_street(),
                         _("Parish: %s ") % location.get_parish(),
                         _("Locality: %s ") % location.get_locality(),
                         _("City: %s ") % location.get_city(),
                         _("County: %s ") % location.get_county(),
                         _("State: %s") % location.get_state(),
                         _("Country: %s ") % location.get_country()]
        self.doc.start_paragraph("PLC-PlaceTitle")
        self.doc.write_text(("%(nbr)s. %(place)s") % 
                                {'nbr' : place_nbr,
                                 'place' : place.get_title()})
        self.doc.end_paragraph()

        for item in place_details:
            self.doc.start_paragraph("PLC-PlaceDetails")
            self.doc.write_text(item) 
            self.doc.end_paragraph()

    def __write_referenced_events(self, handle):
        """
        This procedure writes out each of the events related to the place
        """
        event_handles = [event_handle for (object_type, event_handle) in
                         self.database.find_backlink_handles(handle)]
        event_handles.sort(self.sort.by_date)

        if event_handles:
            self.doc.start_paragraph("PLC-Section")
            title = _("Events that happened at this place")
            self.doc.write_text(title)
            self.doc.end_paragraph()
            self.doc.start_table("EventTable", "PLC-EventTable")
            column_titles = [_("Date"), _("Type of Event"),
                             _("Person"), _("Description")]
            self.doc.start_row()
            for title in column_titles:
                self.doc.start_cell("PLC-TableColumn")
                self.doc.start_paragraph("PLC-ColumnTitle")
                self.doc.write_text(title)
                self.doc.end_paragraph()
                self.doc.end_cell()
            self.doc.end_row()

        for evt_handle in event_handles:
            event = self.database.get_event_from_handle(evt_handle)
            if event:
                date = DateHandler.get_date(event)
                descr = event.get_description()
                event_type = str(event.get_type())

                person_list = []
                ref_handles = [x for x in
                               self.database.find_backlink_handles(evt_handle)]
                for (ref_type, ref_handle) in ref_handles:
                    if ref_type == 'Person':
                        person_list.append(ref_handle)
                    else:
                        family = self.database.get_family_from_handle(ref_handle)
                        father = family.get_father_handle()
                        if father:
                            person_list.append(father)
                        mother = family.get_mother_handle()
                        if mother:
                            person_list.append(mother)

                people = ""
                person_list = list(set(person_list))
                for p_handle in person_list:
                    person = self.database.get_person_from_handle(p_handle)
                    if person:
                        if people == "":
                            people = "%s (%s)" \
                                     % (_nd.display(person),
                                        person.get_gramps_id())
                        else:
                            people = _("%s and %s (%s)") \
                                     % (people, _nd.display(person),
                                        person.get_gramps_id())

                event_details = [date, event_type, people, descr]
                self.doc.start_row()
                for detail in event_details:
                    self.doc.start_cell("PLC-Cell")
                    self.doc.start_paragraph("PLC-Details")
                    self.doc.write_text("%s " % detail)
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                self.doc.end_row()

        if event_handles:
            self.doc.end_table()

    def __write_referenced_persons(self, handle):
        """
        This procedure writes out each of the people related to the place
        """
        event_handles = [event_handle for (object_type, event_handle) in
                         self.database.find_backlink_handles(handle)]

        if event_handles:
            self.doc.start_paragraph("PLC-Section")
            title = _("People associated with this place")
            self.doc.write_text(title)
            self.doc.end_paragraph()
            self.doc.start_table("EventTable", "PLC-PersonTable")
            column_titles = [_("Person"), _("Type of Event"), \
                             _("Description"), _("Date")]
            self.doc.start_row()
            for title in column_titles:
                self.doc.start_cell("PLC-TableColumn")
                self.doc.start_paragraph("PLC-ColumnTitle")
                self.doc.write_text(title)
                self.doc.end_paragraph()
                self.doc.end_cell()
            self.doc.end_row()

        person_dict = {}
        for evt_handle in event_handles:
            ref_handles = [x for x in
                           self.database.find_backlink_handles(evt_handle)]
            for (ref_type, ref_handle) in ref_handles:
                if ref_type == 'Person':
                    person = self.database.get_person_from_handle(ref_handle)
                    nameEntry = "%s (%s)" % (_nd.display(person),
                                             person.get_gramps_id())
                    if person_dict.has_key(nameEntry):
                        person_dict[nameEntry].append(evt_handle)
                    else:
                        person_dict[nameEntry] = []
                        person_dict[nameEntry].append(evt_handle)
                else:
                    family = self.database.get_family_from_handle(ref_handle)
                    f_handle = family.get_father_handle()
                    m_handle = family.get_mother_handle()
                    if f_handle and m_handle:
                        father = self.database.get_person_from_handle(f_handle)
                        mother = self.database.get_person_from_handle(m_handle)
                        nameEntry = "%s (%s) and %s (%s)" % \
                                    (_nd.display(father),
                                     father.get_gramps_id(),
                                     _nd.display(mother),
                                     mother.get_gramps_id())
                    else:
                        if f_handle:
                            p_handle = f_handle
                        else:
                            p_handle = m_handle
                        person = self.database.get_person_from_handle(p_handle)
                        
                        nameEntry = "%s (%s)" % \
                                     (_nd.display(person),
                                      person.get_gramps_id())

                    if person_dict.has_key(nameEntry):
                        person_dict[nameEntry].append(evt_handle)
                    else:
                        person_dict[nameEntry] = []
                        person_dict[nameEntry].append(evt_handle)

        keys = person_dict.keys()
        keys.sort()

        for entry in keys:
            people = entry
            person_dict[entry].sort(self.sort.by_date)
            for evt_handle in person_dict[entry]:
                event = self.database.get_event_from_handle(evt_handle)
                if event:
                    date = DateHandler.get_date(event)
                    descr = event.get_description()
                    event_type = str(event.get_type())
                event_details = [people, event_type, descr, date]
                self.doc.start_row()
                for detail in event_details:
                    self.doc.start_cell("PLC-Cell")
                    self.doc.start_paragraph("PLC-Details")
                    self.doc.write_text("%s " % detail)
                    self.doc.end_paragraph()
                    self.doc.end_cell()
                people = "" # do not repeat the name on the next event
                self.doc.end_row()

        if event_handles:
            self.doc.end_table()
        
    def __get_place_handles(self, places):
        """
        This procedure converts a string of place GIDs to a list of handles
        """
        place_handles = [] 
        for place_gid in places.split():
            place = self.database.get_place_from_gramps_id(place_gid)
            if place is not None:
                #place can be None if option is gid of other fam tree
                place_handles.append(place.get_handle())

        return place_handles
    
#------------------------------------------------------------------------
#
# AncestorOptions
#
#------------------------------------------------------------------------
class PlaceOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """
        Add options to the menu for the place report.
        """
        category_name = _("Report Options")

        # Reload filters to pick any new ones
        CustomFilters = None
        from Filters import CustomFilters, GenericFilter

        opt = FilterOption(_("Select using filter"), 0)
        opt.set_help(_("Select places using a filter"))
        filter_list = []
        filter_list.append(GenericFilter())
        filter_list.extend(CustomFilters.get_filters('Place'))
        opt.set_filters(filter_list)
        menu.add_option(category_name, "filter", opt)

        places = PlaceListOption(_("Select places individually"))
        places.set_help(_("List of places to report on"))
        menu.add_option(category_name, "places", places)

        center = EnumeratedListOption(_("Center on"), "Event")
        center.set_items([
                ("Event",   _("Event")),
                ("Person", _("Person"))])
        center.set_help(_("If report is event or person centered"))
        menu.add_option(category_name, "center", center)

        incpriv = BooleanOption(_("Include private data"), True)
        incpriv.set_help(_("Whether to include private data"))
        menu.add_option(category_name, "incpriv", incpriv)

    def make_default_style(self, default_style):
        """
        Make the default output style for the Place report.
        """
        self.default_style = default_style
        self.__report_title_style()
        self.__place_title_style()
        self.__place_details_style()
        self.__column_title_style()
        self.__section_style()
        self.__event_table_style()
        self.__details_style()
        self.__cell_style()
        self.__table_column_style()

    def __report_title_style(self):
        """
        Define the style used for the report title
        """
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=16, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)       
        para.set_description(_('The style used for the title of the report.'))
        self.default_style.add_paragraph_style("PLC-ReportTitle", para)

    def __place_title_style(self):
        """
        Define the style used for the place title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=12, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=-1.5, lmargin=1.5)
        para.set_top_margin(0.75)
        para.set_bottom_margin(0.25)        
        para.set_description(_('The style used for place title.'))
        self.default_style.add_paragraph_style("PLC-PlaceTitle", para)

    def __place_details_style(self):
        """
        Define the style used for the place details
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_description(_('The style used for place details.'))
        self.default_style.add_paragraph_style("PLC-PlaceDetails", para)

    def __column_title_style(self):
        """
        Define the style used for the event table column title
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=0.0)
        para.set_description(_('The style used for a column title.'))
        self.default_style.add_paragraph_style("PLC-ColumnTitle", para)

    def __section_style(self):
        """
        Define the style used for each section
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10, italic=0, bold=0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=-1.5, lmargin=1.5)
        para.set_top_margin(0.5)
        para.set_bottom_margin(0.25)        
        para.set_description(_('The style used for each section.'))
        self.default_style.add_paragraph_style("PLC-Section", para)

    def __event_table_style(self):
        """
        Define the style used for event table
        """
        table = TableStyle()
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 25)
        table.set_column_width(1, 15)
        table.set_column_width(2, 35)
        table.set_column_width(3, 25)
        self.default_style.add_table_style("PLC-EventTable", table)
        table.set_width(100)
        table.set_columns(4)
        table.set_column_width(0, 35)
        table.set_column_width(1, 15)
        table.set_column_width(2, 25)
        table.set_column_width(3, 25)
        self.default_style.add_table_style("PLC-PersonTable", table)

    def __details_style(self):
        """
        Define the style used for person and event details
        """
        font = FontStyle()
        font.set(face=FONT_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The style used for event and person details.'))
        self.default_style.add_paragraph_style("PLC-Details", para)

    def __cell_style(self):
        """
        Define the style used for cells in the event table
        """
        cell = TableCellStyle()
        self.default_style.add_cell_style("PLC-Cell", cell)

    def __table_column_style(self):
        """
        Define the style used for event table columns
        """
        cell = TableCellStyle()
        cell.set_bottom_border(1)
        self.default_style.add_cell_style('PLC-TableColumn', cell)
