#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
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
PostScript document generator.
"""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#Gramps modules
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.docgen import BaseDoc, DrawDoc, FONT_SERIF, PAPER_PORTRAIT, SOLID
from gramps.gen.errors import ReportError
from gramps.gen.constfunc import cuni

def lrgb(grp):
    return ['%.3f' % x for x in ReportUtils.rgb_color(grp)]

def coords(grp):
    return ['%.3f' % x for x in grp]

#-------------------------------------------------------------------------
#
# PSDrawDoc
#
#-------------------------------------------------------------------------
class PSDrawDoc(BaseDoc, DrawDoc):

    def __init__(self, styles, type):
        BaseDoc.__init__(self, styles, type)
        self.file = None
        self.filename = None
        self.level = 0
        self.page = 0

    def fontdef(self, para):
        font = para.get_font()
        if font.get_type_face() == FONT_SERIF:
            font_name = "/Times"
            if font.get_bold():
                font_name += "-Bold"
                if font.get_italic():
                    font_name += "Italic"
            elif font.get_italic():
                font_name += "-Italic"
            else:
                font_name += "-Roman"

        else: # Use a font without serifs
            font_name = "/Helvetica"
            if font.get_bold():
                font_name += "-Bold"
                if font.get_italic():
                    font_name += "Oblique"
            elif font.get_italic():
                font_name += "-Oblique"
        
        return "%s find-latin-font %d scalefont setfont\n" % \
            (font_name, font.get_size())

    def translate(self, x, y):
        return (x, self.paper.get_size().get_height() - y)

    def open(self, filename):
        """
        Opens the file so that it can be generated.

        @param filename: path name of the file to create
        """
        self.filename = filename
        if not filename.endswith(".ps"):
            self.filename += ".ps"

        try:
            self.file = open(self.filename,"w")
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % self.filename)
        
        self.file.write(
            '%!PS-Adobe-3.0\n'
            '%%LanguageLevel: 2\n'
            '%%Pages: (atend)\n'
            '%%PageOrder: Ascend\n'
            '%%Orientation: '
            )
        if self.paper.get_orientation() != PAPER_PORTRAIT:
            self.file.write('Landscape\n')
        else:
            self.file.write('Portrait\n')
        self.file.write(
            '%%EndComments\n'
            '/cm { 28.34 mul } def\n'
            '%% Copied from http://en.wikibooks.org/wiki/PostScript_FAQ#How_to_concatenate_strings.3F, where it\'s attributed to Ghostscript, which might be why it worked originally\n'
            '/concatstrings % (a) (b) -> (ab)\n'
            '   { exch dup length\n'
            '     2 index length add string\n'
            '     dup dup 4 2 roll copy length\n'
            '     4 -1 roll putinterval\n'
            '   } bind def\n'
            '% build iso-latin-1 version of a font\n'
            '/font-to-iso-latin-1 { % <font> font-to-iso-latin-1 <font>\n'
            '%% reencode for iso latin1; from the 2nd edition red book, sec 5.6.1\n'
            'dup length dict begin {1 index /FID ne {def} {pop pop} ifelse} forall\n'
            '/Encoding ISOLatin1Encoding def currentdict end\n'
            'dup /FontName get 80 string cvs (-ISOLatin1) concatstrings cvn \n'
            'exch definefont\n'
            '} def\n'
            '\n'
            '/find-latin-font { % <name> find-latin-font <font>\n'
            'findfont font-to-iso-latin-1\n'
            '} def\n'
            )
        
        self.filename = filename

    def close(self):
        self.file.write(
            '%%Trailer\n'
            '%%Pages: ' +
            '%d\n' % self.page +
            '%%EOF\n'
            )
        self.file.close()
        
    def write_text(self, text, mark=None, links=False):
        pass

    def start_page(self):
        self.page += 1
        self.file.write(
            "%%Page:" +
            "%d %d\n" % (self.page, self.page)
            )
        if self.paper.get_orientation() != PAPER_PORTRAIT:
            self.file.write('90 rotate %.3f cm %.3f cm translate\n' %
                            (0, -1*self.paper.get_size().get_height()))

    def end_page(self):
        self.file.write(
            'showpage\n'
            '%%PageTrailer\n'
            )

    def encode(self, text):
        try:
            orig = cuni(text)
            new_text = orig.encode('iso-8859-1')
        except:
            new_text = "?" * len(text)
        return new_text

    def encode_text(self, p, text):
        fdef = self.fontdef(p)
        new_text = self.encode(text)
        return (new_text, fdef)

    def center_text(self, style, text, x, y, mark=None):
        """ @param mark:  IndexMark to use for indexing (not supported) """
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)

        x += self.paper.get_left_margin()
        y += self.paper.get_top_margin() + ReportUtils.pt2cm(p.get_font().get_size())

        (text, fdef) = self.encode_text(p, text)

        self.file.write(
            'gsave\n'
            '%.3f %.3f %.3f setrgbcolor\n' % stype.get_color() +
            fdef +
            '(%s) dup stringwidth pop -2 div ' % text +
            '%.3f cm add %.3f cm moveto ' % self.translate(x, y) +
            'show\n'
            'grestore\n'
            )

    def draw_text(self, style, text, x1, y1, mark=None):
        """ @param mark:  IndexMark to use for indexing (not supported) """
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)

        x1 += self.paper.get_left_margin()
        y1 += self.paper.get_top_margin() + ReportUtils.pt2cm(p.get_font().get_size())

        (text, fdef) = self.encode_text(p, text)

        self.file.write(
            'gsave\n'
            '%.3f cm %.3f cm moveto\n' % self.translate(x1, y1) +
            fdef +
            '(%s) show grestore\n' % text
            )

    def rotate_text(self, style, text, x, y, angle, mark=None):
        """ @param mark:  IndexMark to use for indexing (not supported) """

        x += self.paper.get_left_margin()
        y += self.paper.get_top_margin()

        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)
        font = p.get_font()

        size = font.get_size()

        (new_text, fdef) = self.encode_text(p, text[0])

        self.file.write(
            'gsave\n' +
            fdef +
            '%.3f cm %.3f cm translate\n' % self.translate(x, y) +
            '%.3f rotate\n' % -angle +
            '%.3f %.3f %.3f setrgbcolor\n' % stype.get_color()
            )

        y = ((size * len(text)) / 2.0) - size

        for line in text:
            self.file.write(
                '(%s) dup stringwidth pop -2 div  '
                    % self.encode(line) +
                "%.3f moveto show\n" % y
                )
            y -= size
 
        self.file.write('grestore\n')

    def draw_path(self, style, path):
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        self.file.write(
            'gsave\n'
            'newpath\n'
            '%.3f setlinewidth\n' % stype.get_line_width()
            )
        if stype.get_line_style() == SOLID:
            self.file.write('[] 0 setdash\n')
        else:
            dash_style = stype.get_dash_style(stype.get_line_style())
            self.file.write('[%s] 0 setdash\n' % (
                                " ".join(map(str, dash_style)))
                                )

        point = path[0]
        x1 = point[0] + self.paper.get_left_margin()
        y1 = point[1] + self.paper.get_top_margin()
        self.file.write(
            '%.3f cm %.3f cm moveto\n' % self.translate(x1, y1)
            )

        for point in path[1:]:
            x1 = point[0] + self.paper.get_left_margin()
            y1 = point[1] + self.paper.get_top_margin()
            self.file.write(
                '%.3f cm %.3f cm lineto\n' % self.translate(x1, y1)
                )
        self.file.write('closepath\n')

        color = stype.get_fill_color()
        self.file.write(
            'gsave %.3f %.3f %.3f setrgbcolor fill grestore\n' % color +
            '%.3f %.3f %.3f setrgbcolor stroke\n' % stype.get_color() +
            'grestore\n'
            )

    def draw_line(self, style, x1, y1, x2, y2):
        x1 += self.paper.get_left_margin()
        x2 += self.paper.get_left_margin()
        y1 += self.paper.get_top_margin()
        y2 += self.paper.get_top_margin()
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        self.file.write(
            'gsave newpath\n'
            '%.3f cm %.3f cm moveto\n' % self.translate(x1, y1) +
            '%.3f cm %.3f cm lineto\n' % self.translate(x2, y2) +
            '%.3f setlinewidth\n' % stype.get_line_width()
            )
        if stype.get_line_style() == SOLID:
            self.file.write('[] 0 setdash\n')
        else:
            dash_style = stype.get_dash_style(stype.get_line_style())
            self.file.write('[%s] 0 setdash\n' % (
                                " ".join(map(str, dash_style)))
                                )
            
        self.file.write(
            '2 setlinecap\n' +
            '%.3f %.3f %.3f setrgbcolor stroke\n' % stype.get_color() +
            'grestore\n'
            )

    def draw_box(self, style, text, x, y, w, h, mark=None):
        """ @param mark:  IndexMark to use for indexing (not supported) """
        x += self.paper.get_left_margin()
        y += self.paper.get_top_margin()
        
        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)

        self.file.write('gsave\n')

        shadsize = box_style.get_shadow_space()
        if box_style.get_shadow():
            self.file.write(
                'newpath\n'
                '%.3f cm %.3f cm moveto\n'
                    % self.translate(x+shadsize, y+shadsize) +
                '0 -%.3f cm rlineto\n' % h +
                '%.3f cm 0 rlineto\n' % w +
                '0 %.3f cm rlineto\n' % h +
                'closepath\n'
                '.5 setgray\n'
                'fill\n'
                )
        self.file.write(
            'newpath\n' 
            '%.3f cm %.3f cm moveto\n' % self.translate(x, y) +
            '0 -%.3f cm rlineto\n' % h +
            '%.3f cm 0 rlineto\n' % w +
            '0 %.3f cm rlineto\n' % h +
            'closepath\n'
            )
        
        fill_color = box_style.get_fill_color()
        color = box_style.get_color()
        self.file.write(
            'gsave %.3f %.3f %.3f setrgbcolor fill grestore\n' % fill_color +
            '%.3f %.3f %.3f setrgbcolor stroke\n' % color
            )

        self.file.write('newpath\n')
        if box_style.get_line_width():
            self.file.write(
                '%.3f cm %.3f cm moveto\n' % self.translate(x, y) +
                '0 -%.3f cm rlineto\n' % h +
                '%.3f cm 0 rlineto\n' % w +
                '0 %.3f cm rlineto\n' % h +
                'closepath\n' +
                '%.3f setlinewidth\n' % box_style.get_line_width() +
                '%.3f %.3f %.3f setrgbcolor stroke\n' % box_style.get_color()
                )
        if text:
            para_name = box_style.get_paragraph_style()
            assert( para_name != '' )
            p = style_sheet.get_paragraph_style(para_name)
            (text, fdef) = self.encode_text(p, text)
            self.file.write(fdef)
            lines = text.split('\n')

            mar = 10/28.35
            f_in_cm = p.get_font().get_size()/28.35
            fs = f_in_cm * 1.2
            center = y + (h + fs)/2.0 + (fs*shadsize)
            ystart = center - (fs/2.0) * len(lines)
            for i, line in enumerate(lines):
                ypos = ystart + (i * fs)
                self.file.write(
                    '%.3f cm %.3f cm moveto\n'
                        % self.translate(x+mar, ypos) +
                    "(%s) show\n" % lines[i]
                    )
        self.file.write('grestore\n')
