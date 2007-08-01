#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
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

"Text Reports/End of Line Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report, relationship_class
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
from Filters import GenericFilterFactory, Rules
from BasicUtils import name_displayer
import DateHandler

#------------------------------------------------------------------------
#
# EndOfLineReport
#
#------------------------------------------------------------------------
class EndOfLineReport(Report):

    def __init__(self, database, person, options_class):
        """
        Creates the EndOfLineReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.

        """
        Report.__init__(self,database,person,options_class)
        
        self.person = person
        
        plist = self.database.get_person_handles(sort_handles=False)
        FilterClass = GenericFilterFactory('Person')
        filter = FilterClass()
        gid = person.get_gramps_id()
        filter.add_rule(Rules.Person.IsAncestorOf([gid,1]))
        filter.add_rule(Rules.Person.MissingParent([]))
        self.ind_list = filter.apply(self.database,plist)
        
        self.relationship = relationship_class(self.database)

        # eol_map is a map whose:
        #   keys are the generations of the people
        #   values are a map whose:
        #      keys are person handles
        #      values are an array whose:
        #         elements are an array of names that link the person handle 
        #         to the person or interest
        # eol_map[generation][person_handle][pedigree_index][person_name_index]
        #
        # There is an array of pedigrees because one person could show up twice 
        # in one generation (descendants marrying). Most people only have one
        # pedigree.
        #
        # eol_map is populated by get_eol() which calls itself recursively.
        self.eol_map = {}
        self.get_eol(self.person,1,[])
        
    def get_eol(self,person,gen,pedigree):
        name = name_displayer.display(person)
        pedigree = pedigree + [name]
        person_is_eol = False
        families = person.get_parent_family_handle_list()
        
        if not families:
            person_is_eol = True

        for family_handle in families:
            family = self.database.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            if father_handle: 
                father = self.database.get_person_from_handle(father_handle)
                self.get_eol(father,gen+1,pedigree)
            if mother_handle:
                mother =  self.database.get_person_from_handle(mother_handle)
                self.get_eol(mother,gen+1,pedigree)
        
            if not father_handle or not mother_handle:
                person_is_eol = True
                
        if person_is_eol:
            # This person is the end of a line
            person_handle = person.get_handle()
            if not self.eol_map.has_key(gen):
                self.eol_map[gen] = {}
            if not self.eol_map[gen].has_key(person_handle):
                self.eol_map[gen][person_handle] = []
            self.eol_map[gen][person_handle].append( list(pedigree) )
        
        # Remove this person from the pedigree
        pedigree = pedigree[1:len(pedigree)]

    def write_report(self):
        """
        The routine the actually creates the report. At this point, the document
        is opened and ready for writing.
        """
        pname = name_displayer.display(self.person)
        
        self.doc.start_paragraph("EOL-Title")
        title = _("End of Line Report for %s") % pname
        mark = BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,1)
        self.doc.write_text(title,mark)
        self.doc.end_paragraph()
        
        self.doc.start_paragraph("EOL-Subtitle")
        title = _("All the ancestors of %s who are missing a parent") % pname
        self.doc.write_text(title)
        self.doc.end_paragraph()
        
        self.doc.start_table('EolTable','EOL-Table')
        
#        self.write_collumn_header()

        for generation in self.eol_map.keys():
            self.write_generation_row(generation)
            for person_handle in self.eol_map[generation].keys():
                self.write_person_row(person_handle)
                self.write_relationship_row(person_handle)
                for pedigree in self.eol_map[generation][person_handle]:
                    self.write_pedigree_row(pedigree)
        self.doc.end_table()
        
    def write_collumn_header(self):
        """
        Write out a row in the table with the collumn headings.
        """
        self.doc.start_row()

        self.doc.start_cell('EOL-TableCell')
        self.doc.start_paragraph('EOL-Normal-Bold')
        self.doc.write_text(_("Name"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('EOL-TableCell')
        self.doc.start_paragraph('EOL-Normal-Bold')
        self.doc.write_text(_("Birth"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('EOL-TableCell')
        self.doc.start_paragraph('EOL-Normal-Bold')
        self.doc.write_text(_("Death"))
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()
        
    def write_generation_row(self,generation):
        """
        Write out a row in the table showing the generation.
        """
        self.doc.start_row()
        self.doc.start_cell('EOL_GenerationCell',4)
        self.doc.start_paragraph('EOL-Generation')
        self.doc.write_text( _("Generation %d") % generation )
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
    def write_person_row(self,person_handle):
        """
        Write a row in the table with information about the given person.
        """
        person = self.database.get_person_from_handle(person_handle)

        self.doc.start_row()

        name = name_displayer.display(person)
        mark = ReportUtils.get_person_mark(self.database, person)
        self.doc.start_cell('EOL-TableCell')
        self.doc.start_paragraph('EOL-Normal')
        self.doc.write_text(name,mark)
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('EOL-TableCell')
        self.doc.start_paragraph('EOL-Normal')
        birth_ref = person.get_birth_ref()
        if birth_ref:
            event = self.database.get_event_from_handle(birth_ref.ref)
            text = DateHandler.get_date( event )
            
            place_handle = event.get_place_handle()
            place = ReportUtils.place_name(self.database,place_handle)
            if place:
                if text:
                    text += "\n"
                text += place
            
            self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.start_cell('EOL-TableCell')
        self.doc.start_paragraph('EOL-Normal')
        death_ref = person.get_death_ref()
        if death_ref:
            event = self.database.get_event_from_handle(death_ref.ref)
            text = DateHandler.get_date( event )
            
            place_handle = event.get_place_handle()
            place = ReportUtils.place_name(self.database,place_handle)
            if place:
                if text:
                    text += "\n"
                text += place
            
            self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        
        self.doc.end_row()
        
    def write_relationship_row(self,person_handle):
        """
        Write a row in the table with with the person's relationship.
        """
        ancestor = self.database.get_person_from_handle(person_handle)
        (rel_string,common) = self.relationship.get_relationship(
                                             self.person,ancestor)
        
        text = _("%(person)s is the %(relationship)s of %(active_person)s.") % {
                    'person'        : name_displayer.display(ancestor), 
                    'relationship'  : rel_string,
                    'active_person' : name_displayer.display(self.person)      }

        self.doc.start_row()
        self.doc.start_cell('EOL-TableCell')
        self.doc.end_cell()
        self.doc.start_cell('EOL-TableCell',3)
        self.doc.start_paragraph('EOL-Pedigree')
        self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()
        
    def write_pedigree_row(self,pedigree):
        """
        Write a row in the table with with the person's relationship.
        
        pedigree is an array containing the names of the people in the pedigree
        """
        text = " -- ".join(pedigree)
        self.doc.start_row()
        self.doc.start_cell('EOL-TableCell')
        self.doc.end_cell()
        self.doc.start_cell('EOL-TableCell',3)
        self.doc.start_paragraph('EOL-Pedigree')
        self.doc.write_text(text)
        self.doc.end_paragraph()
        self.doc.end_cell()
        self.doc.end_row()

class EndOfLineOptions(ReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def make_default_style(self,default_style):
        """Make the default output style for the End of Line Report."""
        # Paragraph Styles
        f = BaseDoc.FontStyle()
        f.set_size(16)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        f.set_bold(1)
        p = BaseDoc.ParagraphStyle()
        p.set_header_level(1)
        p.set_bottom_border(1)
        p.set_bottom_margin(ReportUtils.pt2cm(8))
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("EOL-Title",p)
        
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,italic=1)
        p = BaseDoc.ParagraphStyle()
        p.set_bottom_margin(ReportUtils.pt2cm(6))
        p.set_font(font)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_('The style used for the section headers.'))
        default_style.add_paragraph_style("EOL-Subtitle",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(10)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(6))
        p.set_bottom_margin(ReportUtils.pt2cm(6))
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("EOL-Normal",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(12)
        font.set_italic(True)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for generation headings.'))
        default_style.add_paragraph_style("EOL-Generation",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(12)
        font.set_bold(True)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for table headings.'))
        default_style.add_paragraph_style("EOL-Normal-Bold",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(8)
        p = BaseDoc.ParagraphStyle()
        p.set_font(font)
        p.set_top_margin(0)
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("EOL-Pedigree",p)
        
        #Table Styles
        cell = BaseDoc.TableCellStyle()
        default_style.add_cell_style('EOL-TableCell',cell)
        
        cell = BaseDoc.TableCellStyle()
        cell.set_bottom_border(1)
        default_style.add_cell_style('EOL_GenerationCell',cell)

        table = BaseDoc.TableStyle()
        table.set_width(100)
        table.set_columns(3)
        table.set_column_width(0,26)
        table.set_column_width(1,37)
        table.set_column_width(2,37)
        default_style.add_table_style('EOL-Table',table)

#------------------------------------------------------------------------
#
# Register the plugin
#
#------------------------------------------------------------------------
register_report(
    name = 'endofline_report',
    category = CATEGORY_TEXT,
    report_class = EndOfLineReport,
    options_class = EndOfLineOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("End of Line Report"),
    status=(_("Stable")),
    description= _("Produces a textual end of line report"),
    author_name="Brian G. Matherly",
    author_email="brian@gramps-project.org"
    )
