#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

"Generate files/Descendant Report"

import os
import re
import sort
import string

import RelLib
import const
import utils
import const
from TextDoc import *
from OpenOfficeDoc import *
from AbiWordDoc import *
from HtmlDoc import *

from gtk import *
from gnome.ui import *
from libglade import *

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendantReport:

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,name,person,db,doc):
        self.creator = db.getResearcher().getName()
        self.name = name
        self.person = person
        self.doc = doc
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):

        f = FontStyle()
        f.set_size(14)
        f.set_type_face(FONT_SANS_SERIF)
        f.set_bold(1)
        p = ParagraphStyle()
        p.set_font(f)
        
        self.doc.add_style("Title",p)

        f = FontStyle()
        for i in range(1,10):
            p = ParagraphStyle()
            p.set_font(f)
            p.set_left_margin(float(i-1))
            self.doc.add_style("Level" + str(i),p)
            
        self.doc.open(self.name)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.doc.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def report(self):
        self.doc.start_paragraph("Title")
        self.doc.write_text('Descendants of ')
        self.doc.write_text(self.person.getPrimaryName().getRegularName())
        self.doc.end_paragraph()
        self.dump(1,self.person)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def dump(self,level,person):
        self.doc.start_paragraph("Level" + str(level))
        self.doc.write_text(str(level) + '. ')
        self.doc.write_text(person.getPrimaryName().getRegularName())

        birth = person.getBirth().getDateObj().get_start_date().getYear()
        death = person.getDeath().getDateObj().get_start_date().getYear()
        if birth != -1 or death != -1:
            self.doc.write_text(' (')
            if birth != -1:
                self.doc.write_text('b. ' + str(birth))
            if death != -1:
                if birth != -1:
                    self.doc.write_text(', ')
                self.doc.write_text('d. ' + str(death))
            self.doc.write_text(')')
        self.doc.end_paragraph()

        for family in person.getFamilyList():
            for child in family.getChildList():
                self.dump(level+1,child)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DesReportWindow:
    def __init__(self,person,db):
        import PaperMenu
        
        self.person = person

        glade_file = os.path.dirname(__file__) + os.sep + "desreport.glade"
        self.top = GladeXML(glade_file,"dialog1")
        self.top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_html_toggled": on_html_toggled,
            "on_save_clicked": on_save_clicked
            })

        PaperMenu.make_paper_menu(self.top.get_widget("papersize"))
        PaperMenu.make_orientation_menu(self.top.get_widget("orientation"))
        
        mytop = self.top.get_widget("dialog1")
        mytop.set_data("o",self)
        mytop.set_data("d",db)
        mytop.show()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    report = DesReportWindow(person,database)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_save_clicked(obj):
    myobj = obj.get_data("o")
    db = obj.get_data("d")

    file = myobj.top.get_widget("fileentry1").get_full_path(0)
    if file == "":
        return

    paper_obj = myobj.top.get_widget("papersize")
    paper = paper_obj.get_menu().get_active().get_data("i")

    orien_obj = myobj.top.get_widget("orientation")
    orien = orien_obj.get_menu().get_active().get_data("i")

    if myobj.top.get_widget("openoffice").get_active():
        document = OpenOfficeDoc(paper,orien)
    elif myobj.top.get_widget("abiword").get_active():
        document = AbiWordDoc(paper,orien)
    else:
        return

    report = DescendantReport(file,myobj.person,db,document)
    report.setup()
    report.report()
    report.end()

    utils.destroy_passed_object(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_html_toggled(obj):
    myobj = obj.get_data("o")
    if myobj.top.get_widget("html").get_active():
        myobj.top.get_widget("htmltemplate").set_sensitive(1)
        myobj.top.get_widget("papersize").set_sensitive(0)
        myobj.top.get_widget("orientation").set_sensitive(0)
    else:
        myobj.top.get_widget("htmltemplate").set_sensitive(0)
        myobj.top.get_widget("papersize").set_sensitive(1)
        myobj.top.get_widget("orientation").set_sensitive(1)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_description():
    return "Generates a list of descendants of the active person"
    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 4 1",
        " 	c None",
        ".	c #FFFFFF",
        "+	c #C0C0C0",
        "@	c #000000",
        "                                                ",
        "                                                ",
        "                                                ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@..................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +............@@@@@@@@@@@.........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "                                                ",
        "                                                ",
        "                                                "]
