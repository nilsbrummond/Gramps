#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Pubilc License as published by
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

"Web Site/Generate Web Site"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import time
import locale
import shutil
import codecs
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS module
#
#------------------------------------------------------------------------
import os
import RelLib
import const
import GrampsKeys
import GenericFilter
import Sort
import Report
import Errors
import Utils
from QuestionDialog import ErrorDialog
import ReportOptions
import BaseDoc
from NameDisplay import displayer as _nd
from DateHandler import displayer as _dd
import ReportUtils
import sets

_NARRATIVE = "narrative.css"
_NAME_COL  = 3

_character_sets = [
    [_('Unicode (recommended)'), 'utf-8'],
    ['ISO-8859-1',  'iso-8859-1' ],
    ['ISO-8859-2',  'iso-8859-2' ],
    ['ISO-8859-3',  'iso-8859-3' ],
    ['ISO-8859-4',  'iso-8859-4' ],
    ['ISO-8859-5',  'iso-8859-5' ],
    ['ISO-8859-6',  'iso-8859-6' ],
    ['ISO-8859-7',  'iso-8859-7' ],
    ['ISO-8859-8',  'iso-8859-8' ],
    ['ISO-8859-9',  'iso-8859-9' ],
    ['ISO-8859-10', 'iso-8859-10' ],
    ['ISO-8859-13', 'iso-8859-13' ],
    ['ISO-8859-14', 'iso-8859-14' ],
    ['ISO-8859-15', 'iso-8859-15' ],
    ['koi8_r',      'koi8_r',     ],
    ]


_css = [
    'BODY {\nfont-family: "Arial", "Helvetica", sans-serif;',
    'letter-spacing: 0.05em;\nbackground-color: #fafaff;',
    'color: #003;\n}',
    'P,BLOCKQUOTE {\nfont-size: 14px;\n}',
    'DIV {\nmargin: 2px;\npadding: 2px;\n}',
    'TD {\nvertical-align: top;\n}',
    'H1 {',
    'font-family: "Verdana", "Bistream Vera Sans", "Arial", "Helvetica", sans-serif;',
    'font-weight: bolder;\nfont-size: 160%;\nmargin: 2px;\n}\n',
    'H2 {',
    'font-family: "Verdana", "Bistream Vera Sans", "Arial", "Helvetica", sans-serif;',
    'font-weight: bolder;\nfont-style: italic;\nfont-size: 150%;\n}',
    'H3 {\nfont-weight: bold;\nmargin: 0;\npadding-top: 10px;',
    'padding-bottom: 10px;\ncolor: #336;\n}',
    'H4 {\nmargin-top: 1em;\nmargin-bottom: 0.3em;',
    'padding-left: 4px;\nbackground-color: #667;\ncolor: #fff;\n}',
    'H5 {\nmargin-bottom: 0.5em;\n}',
    'H6 {\nfont-weight: normal;\nfont-style: italic;',
    'font-size: 100%;\nmargin-left: 1em;\nmargin-top: 1.3em;',
    'margin-bottom: 0.8em;\n}',
    'HR {\nheight: 0;\nwidth: 0;\nmargin: 0;\nmargin-top: 1px;',
    'margin-bottom: 1px;\npadding: 0;\nborder-top: 0;',
    'border-color: #e0e0e9;\n}',
    'A:link {\ncolor: #006;\ntext-decoration: underline;\n}',
    'A:visited {\ncolor: #669;\ntext-decoration: underline;\n}',
    'A:hover {\nbackground-color: #eef;\ncolor: #000;',
    'text-decoration: underline;\n}',
    'A:active {\nbackground-color: #eef;\ncolor: #000;\ntext-decoration: none;\n}',
    '.navheader {\npadding: 4px;\nbackground-color: #e0e0e9;',
    'margin: 2px;\n}',
    '.navtitle {\nfont-size: 160%;\ncolor: #669;\nmargin: 2px;\n}',
    '.navbyline {\nfloat: right;\nfont-size: 14px;\nmargin: 2px;',
    'padding: 4px;\n}',
    '.nav {\nmargin: 0;\nmargin-bottom: 4px;\npadding: 0;',
    'font-size: 14px;\nfont-weight: bold;\n}',
    '.summaryarea {',
    'min-height: 100px;',
    'height: expression(document.body.clientHeight < 1 ? "100px" : "100px" );',
    '}',
    '.portrait {\njustify: center;\nmargin: 5px;\nmargin-right: 20px;',
    'padding: 3px;\nborder-color: #336;\nborder-width: 1px;\n}',
    '.snapshot {\nfloat: right;\nmargin: 5px;\nmargin-right: 20px;',
    'padding: 3px;\n}',
    '.thumbnail {\nheight: 100px;\nborder-color: #336;\nborder-width: 1px;\n}',
    '.leftwrap {\nfloat: left;\nmargin: 2px;\nmargin-right: 10px;\n}',
    '.rightwrap {\nfloat: right;\nmargin: 2px;\nmargin-left: 10px;\n}',
    'TABLE.infolist {\nborder: 0;\nfont-size: 14px;\n}',
    'TD.category {\npadding: 3px;\npadding-right: 3em;',
    'font-weight: bold;\n}',
    'TD.field {\npadding: 3px;\npadding-right: 3em;\n}',
    'TD.data {\npadding: 3px;\npadding-right: 3em;',
    'font-weight: bold;\n}',
    '.pedigree {\nmargin: 0;\nmargin-left: 2em;\npadding: 0;',
    'background-color: #e0e0e9;\nborder: 1px;\n}',
    '.pedigreeind {\nfont-size: 14px;\nmargin: 0;\npadding: 2em;',
    'padding-top: 0.25em;\npadding-bottom: 0.5em;\n}',
    '.footer {\nmargin: 1em;\nfont-size: 12px;\nfloat: right;\n}',
    ]


from cStringIO import StringIO

class BasePage:
    def __init__(self, title, options, archive):
        self.title_str = title
        self.inc_contact = options.handler.options_dict['NWEBcontact']
        self.inc_download = options.handler.options_dict['NWEBdownload']
        self.html_dir = options.handler.options_dict['NWEBod']
        self.options = options
        self.archive = archive
        self.image_dir = options.handler.options_dict['NWEBimagedir'].strip()
        self.ext = options.handler.options_dict['NWEBext']
        self.encoding = options.handler.options_dict['NWEBencoding']
        self.noid = options.handler.options_dict['NWEBnoid']
        
    def copy_media(self,photo):
        newpath = photo.gramps_id + os.path.splitext(photo.get_path())[1]
        if self.image_dir:
            newpath = os.path.join(self.image_dir,newpath)
        if self.archive:
            imagefile = open(photo.get_path(),"r")
            self.archive.add_file(newpath,time.time(),imagefile)
            imagefile.close()
        else:
            shutil.copyfile(photo.get_path(),
                            os.path.join(self.html_dir,newpath))
        return newpath
        
    def create_file(self,name):
        if self.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io,self.encoding)
            self.cur_name = name + "." + self.ext
        else:
            page_name = os.path.join(self.html_dir,name + "." + self.ext)
            of = codecs.EncodedFile(open(page_name, "w"),self.encoding)
        return of

    def close_file(self,of):
        if self.archive:
            self.archive.add_file(self.cur_name,time.time(),self.string_io)
            of.close()
        else:
            of.close()

    def lnkfmt(self,text):
        return text.replace(' ','%20')

    def display_footer(self,of):

        format = locale.nl_langinfo(locale.D_FMT)
        value = time.strftime(format,time.localtime(time.time()))

        msg = _('Generated by <a href="http://gramps-project.org">'
                'GRAMPS</a> on %(date)s' % { 'date' : value })
        
        of.write(u'<br><br><hr>\n')
        of.write(u'<div class="footer">%s</div>\n' % msg)
        of.write(u'</body>\n')
        of.write(u'</html>\n')
    
    def display_header(self,of,title,author=""):

        if author:
            author = author.replace(',,,','')
            year = time.localtime(time.time())[0]
            cright = _(u'Copyright &copy; %(person)s %(year)d') % {
                'person' : author,
                'year' : year }
        
        of.write(u'<!DOCTYPE HTML PUBLIC ')
        of.write(u'"-//W3C//DTD HTML 4.01 Transitional//EN">\n')
        of.write(u'<html>\n<head>\n')
        of.write(u'<title>%s</title>\n' % self.title_str)
        of.write(u'<meta http-equiv="Content-Type" content="text/html; ')
        of.write(u'charset=%s">\n' % self.encoding)
        of.write(u'<link href="%s" ' % _NARRATIVE)
        of.write(u'rel="stylesheet" type="text/css">\n')
        of.write(u'<link href="favicon.png" rel="Shortcut Icon">\n')
        of.write(u'</head>\n')
        of.write(u'<body>\n')
        of.write(u'<div class="navheader">\n')
        if author:
            of.write(u'  <div class="navbyline">%s</div>\n' % cright)
        of.write(u'  <h1 class="navtitle">%s</h1>\n' % self.title_str)
        of.write(u'  <hr>\n')
        of.write(u'    <div class="nav">\n')
        of.write(u'    <a href="index.%s">%s</a> &nbsp;\n' % (self.ext,_('Home')))
        of.write(u'    <a href="introduction.%s">%s</a> &nbsp;\n' % (self.ext,_('Introduction')))
        of.write(u'    <a href="surnames.%s">%s</a> &nbsp;\n' % (self.ext,_('Surnames')))
        of.write(u'    <a href="individuals.%s">%s</a> &nbsp;\n' % (self.ext,_('Individuals')))
        of.write(u'    <a href="sources.%s">%s</a> &nbsp;\n' % (self.ext,_('Sources')))
        of.write(u'    <a href="places.%s">%s</a> &nbsp;\n' % (self.ext,_('Places')))
        if self.inc_download:
            of.write(u'    <a href="download.%s">%s</a> &nbsp;\n' % (self.ext,_('Download')))
        if self.inc_contact:
            of.write(u'    <a href="contact.%s">%s</a> &nbsp;\n' % (self.ext,_('Contact')))
        of.write(u'    </div>\n')
        of.write(u'  </div>\n')

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualListPage(BasePage):

    def __init__(self, db, title, person_handle_list, options, archive):
        BasePage.__init__(self, title, options, archive)

        of = self.create_file("individuals")
        self.display_header(of,_('Individuals'),
                            db.get_researcher().get_name())

        msg = _("This page contains an index of all the individuals in the "
                "database, sorted by their last names. Selecting the GRAMPS "
                "ID next to a person's name will take you to that person's "
                "individual page.")

        of.write(u'<h3>%s</h3>\n' % _('Individuals'))
        of.write(u'<p>%s</p>\n' % msg)
        of.write(u'<blockquote>\n')
        of.write(u'<table class="infolist" cellspacing="0" ')
        of.write(u'cellpadding="0" border="0">\n')
        of.write(u'<tr><td class="field"><u><b>%s</b></u></td>\n' % _('Surname'))
        of.write(u'<td class="field"><u><b>%s</b></u></td>\n' % _('Name'))
        of.write(u'</tr>\n')

        flist = sets.Set(person_handle_list)

        person_handle_list = sort_people(db,person_handle_list)
        
        for (surname,handle_list) in person_handle_list:
            first = True
            of.write(u'<tr><td colspan="2">&nbsp;</td></tr>\n')
            for person_handle in handle_list:
                person = db.get_person_from_handle(person_handle)
                of.write(u'<tr><td class="category">')
                if first:
                    of.write(u'<a name="%s">%s</a>' % (self.lnkfmt(surname),surname))
                else:
                    of.write(u'&nbsp')
                of.write(u'</td><td class="data">')
                of.write(u' <a href="%s.%s">' % (person.gramps_id,self.ext))
                of.write(person.get_primary_name().get_first_name())
                if not self.noid:
                    of.write(u"&nbsp;[%s]" % person.gramps_id)
                of.write(u'</a></td></tr>\n')
                first = False
            
        of.write(u'</table>\n</blockquote>\n')
        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PlaceListPage(BasePage):

    def __init__(self, db, title, place_handles, src_list, options, archive):
        BasePage.__init__(self, title, options, archive)
        of = self.create_file("places")
        self.display_header(of,_('Places'),
                            db.get_researcher().get_name())

        msg = _("This page contains an index of all the places in the "
                "database, sorted by their title. Clicking on a place's "
                "title will take you to that place's page.")

        of.write(u'<h3>%s</h3>\n' % _('Places'))
        of.write(u'<p>%s</p>\n' % msg )

        of.write(u'<blockquote>\n')
        of.write(u'<table class="infolist" cellspacing="0" ')
        of.write(u'cellpadding="0" border="0">\n')
        of.write(u'<tr><td class="field"><u>')
        of.write(u'<b>%s</b></u></td>\n' % _('Letter'))
        of.write(u'<td class="field"><u>')
        of.write(u'<b>%s</b></u></td>\n' % _('Place'))
        of.write(u'</tr>\n')

        self.sort = Sort.Sort(db)
        handle_list = list(place_handles)
        handle_list.sort(self.sort.by_place_title)
        last_name = ""
        last_letter = ''
        
        for handle in handle_list:
            place = db.get_place_from_handle(handle)
            n = ReportUtils.place_name(db,handle)

            if not n or len(n) == 0:
                continue
            
            if n[0] != last_letter:
                last_letter = n[0]
                of.write(u'<tr><td colspan="2">&nbsp;</td></tr>\n')
                of.write(u'<tr><td class="category">%s</td>' % last_letter)
                of.write(u'<td class="data">')
                of.write(u'<a href="%s.%s">' % (place.gramps_id,self.ext))
                of.write(n)
                if not self.noid:
                    of.write(u'&nbsp;[%s]' % place.gramps_id)
                of.write(u'</a></td></tr>')
                last_surname = n
            elif n != last_surname:
                of.write(u'<tr><td class="category">&nbsp;</td>')
                of.write(u'<td class="data">')
                of.write(u'<a href="%s.%s">' % (place.gramps_id,self.ext))
                of.write(n)
                if not self.noid:
                    of.write(u'&nbsp;[%s]' % place.gramps_id)
                of.write(u'</a></td></tr>')
                last_surname = n
            
        of.write(u'</table>\n</blockquote>\n')
        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PlacePage(BasePage):

    def __init__(self, db, title, place_handle, src_list, options, archive):
        place = db.get_place_from_handle( place_handle)
        BasePage.__init__(self,title,options,archive)
        of = self.create_file(place.get_gramps_id())
        place_name = ReportUtils.place_name(db,place_handle)
        self.display_header(of,place_name,
                            db.get_researcher().get_name())
        of.write(u'<h3>%s</h3>\n' % place_name)

        photolist = place.get_media_list()
        if photolist:
            photo_handle = photolist[0].get_reference_handle()
            photo = db.get_object_from_handle(photo_handle)
            
            try:
                newpath = self.copy_media(photo)
                of.write(u'<div class="snapshot">\n')
                of.write(u'<a href="%s">' % newpath)
                of.write(u'<img class="thumbnail"  border="0" src="%s" ' % newpath)
                of.write(u'height="100"></a>')
                of.write(u'</div>\n')
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))

        # TODO: Add more information

        of.write('<h4>%s</h4>\n' % _('Narrative'))
        of.write('<hr>\n')

        noteobj = place.get_note_object()
        if noteobj:
            format = noteobj.get_format()
            text = noteobj.get()

            if format:
                text = u"<pre>" + u"<br>".join(text.split("\n"))
            else:
                text = u"</p><p>".join(text.split("\n"))
            of.write(u'<p>%s</p>\n' % text)

        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SurnameListPage(BasePage):

    def __init__(self, db, title, person_handle_list, options, archive):
        BasePage.__init__(self, title, options, archive)
        of = self.create_file("surnames")
        self.display_header(of,_('Surnames'),
                            db.get_researcher().get_name())

        of.write(u'<h3>%s</h3>\n' % _('Surnames'))
        of.write(u'<p>%s</p>\n' % _(
            'This page contains an index of all the '
            'surnames in the database. Selecting a link '
            'will lead to a list of individuals in the '
            'database with this same surname.'))

        of.write(u'<blockquote>\n')
        of.write(u'<table class="infolist" cellspacing="0" ')
        of.write(u'cellpadding="0" border="0">\n')
        of.write(u'<tr><td class="field"><u>')
        of.write(u'<b>%s</b></u></td>\n' % _('Letter'))
        of.write(u'<td class="field"><u>')
        of.write(u'<b>%s</b></u></td>\n' % _('Surname'))
        of.write(u'</tr>\n')

        person_handle_list = sort_people(db,person_handle_list)
        last_letter = ''
        last_surname = ''
        
        for (surname,data_list) in person_handle_list:
            if len(surname) == 0:
                continue
            
            if surname[0] != last_letter:
                last_letter = surname[0]
                of.write(u'<tr><td class="category">%s</td>' % last_letter)
                of.write(u'<td class="data">')
                of.write(u'<a href="individuals.%s#%s">' % (self.ext,self.lnkfmt(surname)))
                of.write(surname)
                of.write(u'</a></td></tr>')
            elif surname != last_surname:
                of.write(u'<tr><td class="category">&nbsp;</td>')
                of.write(u'<td class="data">')
                of.write(u'<a href="individuals.%s#%s">' % (self.ext,self.lnkfmt(surname)))
                of.write(surname)
                of.write(u'</a></td></tr>')
                last_surname = surname
            
        of.write(u'</table>\n</blockquote>\n')
        self.display_footer(of)
        self.close_file(of)
        return

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IntroductionPage(BasePage):

    def __init__(self, db, title, options, archive):
        BasePage.__init__(self, title, options, archive)
        note_id = options.handler.options_dict['NWEBintronote']

        of = self.create_file("introduction")
        self.display_header(of,_('Introduction'),
                            db.get_researcher().get_name())

        of.write(u'<h3>%s</h3>\n' % _('Introduction'))

        if note_id:
            obj = db.get_object_from_gramps_id(note_id)
            if obj:
                note_obj = obj.get_note_object()
                text = note_obj.get()
                if note_obj.get_format():
                    of.write(u'<pre>\n%s\n</pre>\n' % text)
                else:
                    of.write(u'<p>')
                    of.write(u'</p><p>'.join(text.split('\n')))
                    of.write(u'</p>')

        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class HomePage(BasePage):

    def __init__(self, db, title, options, archive):
        BasePage.__init__(self, title, options, archive)
        note_id = options.handler.options_dict['NWEBhomenote']

        of = self.create_file("index")
        self.display_header(of,_('Home'),
                            db.get_researcher().get_name())

        of.write('<h3>%s</h3>\n' % _('Home'))

        if note_id:
            obj = db.get_object_from_handle(note_id)

            if obj:
                mime_type = obj.get_mime_type()
                if mime_type and mime_type.startswith("image"):
                    try:
                        newpath = self.copy_media(obj)
                        of.write(u'<div align="center">\n')
                        of.write(u'<img border="0" ')
                        of.write(u'src="%s" />' % newpath)
                        of.write(u'</div>\n')
                    except (IOError,OSError),msg:
                        ErrorDialog(str(msg))
    
                note_obj = obj.get_note_object()
                if note_obj:
                    text = note_obj.get()
                    if note_obj.get_format():
                        of.write(u'<pre>\n%s\n</pre>\n' % text)
                    else:
                        of.write(u'<p>')
                        of.write(u'</p><p>'.join(text.split('\n')))
                        of.write(u'</p>')

        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SourcesPage(BasePage):

    def __init__(self, db, title, handle_set, options, archive):
        BasePage.__init__(self, title, options, archive)

        of = self.create_file("sources")
        self.display_header(of,_('Sources'),
                            db.get_researcher().get_name())

        handle_list = list(handle_set)

        of.write(u'<h3>%s</h3>\n<p>' % _('Sources'))
        of.write(_('All sources cited in the project.'))
        of.write(u'</p>\n<blockquote>\n<table class="infolist">\n')

        index = 1
        for handle in handle_list:
            source = db.get_source_from_handle(handle)
            of.write(u'<tr><td class="category">%d.</td>\n' % index)
            of.write(u'<td class="data">')
            of.write(source.get_title())
            of.write(u'</td></tr>\n')
            index += 1
            
        of.write(u'</table>\n<blockquote>\n')

        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DownloadPage(BasePage):

    def __init__(self, db, title, options, archive):
        BasePage.__init__(self, title, options, archive)

        of = self.create_file("download")
        self.display_header(of,_('Download'),
                            db.get_researcher().get_name())

        of.write(u'<h3>%s</h3>\n' % _('Download'))

        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ContactPage(BasePage):

    def __init__(self, db, title, options, archive):
        BasePage.__init__(self, title, options, archive)

        of = self.create_file("contact")
        self.display_header(of,_('Contact'),
                            db.get_researcher().get_name())

        of.write(u'<h3>%s</h3>\n' % _('Contact'))

        self.display_footer(of)
        self.close_file(of)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class IndividualPage(BasePage):

    gender_map = {
        RelLib.Person.MALE    : const.male,
        RelLib.Person.FEMALE  : const.female,
        RelLib.Person.UNKNOWN : const.unknown,
        }
    
    def __init__(self, db, person, title, ind_list,
                 place_list, src_list, options, archive):
        BasePage.__init__(self, title, options, archive)
        self.person = person
        self.db = db
        self.ind_list = ind_list
        self.src_list = src_list
        self.place_list = place_list
        self.sort_name = _nd.sorted(self.person)
        self.name = _nd.sorted(self.person)
        
        of = self.create_file(person.gramps_id)
        self.display_header(of, title,
                            self.db.get_researcher().get_name())
        self.display_ind_general(of)
        self.display_ind_events(of)
        self.display_ind_relationships(of)
        self.display_ind_narrative(of)
        self.display_ind_sources(of)
        self.display_ind_pedigree(of)
        self.display_footer(of)
        self.close_file(of)

    def display_ind_sources(self,of):
        sreflist = self.person.get_source_references()
        if not sreflist:
            return
        of.write(u'<h4>%s</h4>\n' % _('Sources'))
        of.write(u'<hr>\n')
        of.write(u'<table class="infolist" cellpadding="0" ')
        of.write(u'cellspacing="0" border="0">\n')

        index = 1
        for sref in sreflist:
            self.src_list.add(sref.get_base_handle())

            source = self.db.get_source_from_handle(sref.get_base_handle())
            author = source.get_author()
            title = source.get_title()
            publisher = source.get_publication_info()
            date = _dd.display(sref.get_date_object())
            of.write(u'<tr><td class="field">%d. ' % index)
            values = []
            if author:
                values.append(author)
            if title:
                values.append(title)
            if publisher:
                values.append(publisher)
            if date:
                values.append(date)
            of.write(u', '.join(values))
            of.write(u'</td></tr>\n')
        of.write(u'</table>\n')

    def display_ind_pedigree(self,of):

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            (parent_handle, mrel,frel) = parent_handle_list[0]
            family = self.db.get_family_from_handle(parent_handle)
            father_id = family.get_father_handle()
            mother_id = family.get_mother_handle()
            mother = self.db.get_person_from_handle(mother_id)
            father = self.db.get_person_from_handle(father_id)
        else:
            family = None
            father = None
            mother = None
        
        of.write(u'<h4>%s</h4>\n' % _('Pedigree'))
        of.write(u'<hr>\n<br>\n')
        of.write(u'<table class="pedigree">\n')
        of.write(u'<tr><td>\n')
        if father or mother:
            of.write(u'<blockquote class="pedigreeind">\n')
            if father:
                self.pedigree_person(of,father)
            if mother:
                self.pedigree_person(of,mother)
        of.write(u'<blockquote class="pedigreeind">\n')
        if family:
            for child_handle in family.get_child_handle_list():
                if child_handle == self.person.handle:
                    of.write(u'| <strong>%s</strong><br>\n' % self.name)
                    self.pedigree_family(of)
                else:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(of,child)
        else:
            of.write(u'| <strong>%s</strong><br>\n' % self.name)
            self.pedigree_family(of)

        of.write(u'</blockquote>\n')
        if father or mother:
            of.write(u'</blockquote>\n')
        of.write(u'</td>\n</tr>\n</table>\n')


    def display_ind_general(self,of):
        photolist = self.person.get_media_list()
        if photolist:
            photo_handle = photolist[0].get_reference_handle()
            photo = self.db.get_object_from_handle(photo_handle)
            
            try:
                newpath = self.copy_media(photo)
                of.write(u'<div class="snapshot">\n')
                of.write(u'<a href="%s">' % newpath)
                of.write(u'<img class="thumbnail"  border="0" src="%s" ' % newpath)
                of.write(u'height="100"></a>')
                of.write(u'</div>\n')
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))

        of.write(u'<div class="summaryarea">\n')
        of.write(u'<h3>%s</h3>\n' % self.sort_name)
        of.write(u'<table class="infolist" cellpadding="0" cellspacing="0" ')
        of.write(u'border="0">\n')

        # Gender
        of.write(u'<tr><td class="field">%s</td>\n' % _('Gender'))
        gender = self.gender_map[self.person.gender]
        of.write(u'<td class="data">%s</td>\n' % gender)
        of.write(u'</tr>\n')

        # Birth
        handle = self.person.get_birth_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            of.write(u'<tr><td class="field">%s</td>\n' % _('Birth'))
            of.write(u'<td class="data">%s</td>\n' % self.format_event(event))
            of.write(u'</tr>\n')

        # Death
        handle = self.person.get_death_handle()
        if handle:
            event = self.db.get_event_from_handle(handle)
            of.write(u'<tr><td class="field">%s</td>\n' % _('Death'))
            of.write(u'<td class="data">%s</td>\n' % self.format_event(event))
            of.write(u'</tr>\n')

        of.write(u'</table>\n')
        of.write(u'</div>\n')

    def display_ind_events(self,of):
        of.write(u'<h4>%s</h4>\n' % _('Events'))
        of.write(u'<hr>\n')
        of.write(u'<table class="infolist" cellpadding="0" cellspacing="0" ')
        of.write(u'border="0">\n')

        for event_id in self.person.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            of.write(u'<tr><td class="field">%s</td>\n' % event.get_name())
            of.write(u'<td class="data">\n')
            of.write(self.format_event(event))
            of.write(u'</td>\n')
            of.write(u'</tr>\n')

        of.write(u'</table>\n')

    def display_ind_narrative(self,of):
        of.write(u'<h4>%s</h4>\n' % _('Narrative'))
        of.write(u'<hr>\n')

        noteobj = self.person.get_note_object()
        if noteobj:
            format = noteobj.get_format()
            text = noteobj.get()

            if format:
                text = u"<pre>" + u"<br>".join(text.split("\n"))
            else:
                text = u"</p><p>".join(text.split("\n"))
            of.write(u'<p>%s</p>\n' % text)

        
    def display_parent(self,of,handle,title):
        use_link = handle in self.ind_list
        person = self.db.get_person_from_handle(handle)
        of.write(u'<td class="field">%s</td>\n' % title)
        of.write(u'<td class="data">')
        val = person.gramps_id
        if use_link:
            of.write('<a href="%s.%s">' % (val,self.ext))           
        of.write(_nd.display(person))
        if not self.noid:
            of.write(u'&nbsp;[%s]' % (val))
        if use_link:
            of.write('</a>')
        of.write(u'</td>\n')

    def display_ind_relationships(self,of):
        parent_list = self.person.get_parent_family_handle_list()
        family_list = self.person.get_family_handle_list()

        if not parent_list and not family_list:
            return
        
        of.write(u'<h4>%s</h4>\n' % _("Relationships"))
        of.write(u'<hr>\n')
        of.write(u'<table class="infolist" cellpadding="0" ')
        of.write(u'cellspacing="0" border="0">\n')

        if parent_list:
            for (family_handle,mrel,frel) in parent_list:
                family = self.db.get_family_from_handle(family_handle)
                
                of.write(u'<tr><td colspan="3">&nbsp;</td></tr>\n')
                of.write(u'<tr><td class="category">%s</td>\n' % _("Parents"))

                father_handle = family.get_father_handle()
                if father_handle:
                    self.display_parent(of,father_handle,_('Father'))
                of.write(u'</tr><tr><td>&nbsp;</td>\n')
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    self.display_parent(of,mother_handle,_('Mother'))
                of.write(u'</tr>\n')
            of.write(u'<tr><td colspan="3">&nbsp;</td></tr>\n')

        if family_list:
            of.write(u'<tr><td class="category">%s</td>\n' % _("Spouses"))
            first = True
            for family_handle in family_list:
                family = self.db.get_family_from_handle(family_handle)
                self.display_spouse(of,family,first)
                first = False
                childlist = family.get_child_handle_list()
                if childlist:
                    of.write(u'<tr><td>&nbsp;</td>\n')
                    of.write(u'<td class="field">%s</td>\n' % _("Children"))
                    of.write(u'<td class="data">\n')
                    for child_handle in childlist:
                        use_link = child_handle in self.ind_list
                        child = self.db.get_person_from_handle(child_handle)
                        gid = child.get_gramps_id()
                        if use_link:
                            of.write(u'<a href="%s.%s">' % (gid,self.ext))
                        of.write(_nd.display(child))
                        if not self.noid:
                            of.write(u'&nbsp;[%s]' % gid)
                        if use_link:
                            of.write(u'</a>\n')
                        of.write(u"<br>\n")
                    of.write(u'</td>\n</tr>\n')
        of.write(u'</table>\n')

    def display_spouse(self,of,family,first=True):
        gender = self.person.get_gender()
        reltype = family.get_relationship()

        if reltype == RelLib.Family.MARRIED:
            if gender == RelLib.Person.FEMALE:
                relstr = _("Husband")
            elif gender == RelLib.Person.MALE:
                relstr = _("Wife")
            else:
                relstr = _("Partner")
        else:
            relstr = _("Partner")

        spouse_id = ReportUtils.find_spouse(self.person,family)
        if spouse_id:
            spouse = self.db.get_person_from_handle(spouse_id)
            name = _nd.display(spouse)
        else:
            name = _("unknown")
        if not first:
            of.write(u'<tr><td>&nbsp;</td></tr>\n')
            of.write(u'<td>&nbsp;</td>')
        of.write(u'<td class="field">%s</td>\n' % relstr)
        of.write(u'<td class="data">')
        if spouse_id:
            use_link = spouse_id in self.ind_list
            gid = spouse.get_gramps_id()
            if use_link:
                of.write(u'<a href="%s.%s">' % (gid,self.ext))
            of.write(name)
            if not self.noid:
                of.write(u'&nbsp;[%s]' % (gid))
            if use_link:
                of.write(u'</a>')
        
        of.write(u'</td>\n</tr>\n')

        for event_id in family.get_event_list():
            event = self.db.get_event_from_handle(event_id)

            of.write(u'<tr><td>&nbsp;</td>\n')
            of.write(u'<td class="field">%s</td>\n' % event.get_name())
            of.write(u'<td class="data">\n')
            of.write(self.format_event(event))
            of.write(u'</td>\n</tr>\n')

    def pedigree_person(self,of,person,bullet='|'):
        person_link = person.handle in self.ind_list
        of.write(u'%s ' % bullet)
        if person_link:
            of.write(u'<a href="%s.%s">' % (person.gramps_id,self.ext))
        of.write(_nd.display(person))
        if person_link:
            of.write(u'</a>')
        of.write(u'<br>\n')

    def pedigree_family(self,of):
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person,rel_family)
            if spouse_handle:
                spouse = self.db.get_person_from_handle(spouse_handle)
                self.pedigree_person(of,spouse,'&bull;')
            childlist = rel_family.get_child_handle_list()
            if childlist:
                of.write(u'<blockquote class="pedigreeind">\n')
                for child_handle in childlist:
                    child = self.db.get_person_from_handle(child_handle)
                    self.pedigree_person(of,child)
                of.write(u'</blockquote>\n')

    def format_event(self,event):
        for sref in event.get_source_references():
            self.src_list.add(sref.get_base_handle())
        descr = event.get_description()
        place_handle = event.get_place_handle()
        if place_handle:
            self.place_list.add(place_handle)
        place = ReportUtils.place_name(self.db,place_handle)

        date = _dd.display(event.get_date_object())
        tmap = {'description' : descr, 'date' : date, 'place' : place}
        
        if descr and date and place:
            text = _('%(description)s, &nbsp;&nbsp; %(date)s &nbsp;&nbsp; at &nbsp&nbsp; %(place)s') % tmap
        elif descr and date:
            text = _('%(description)s, &nbsp;&nbsp; %(date)s &nbsp;&nbsp;') % tmap
        elif descr:
            text = descr
        elif date and place:
            text = _('%(date)s &nbsp;&nbsp; at &nbsp&nbsp; %(place)s') % tmap
        elif date:
            text = date
        elif place:
            text = place
        else:
            text = '\n'
        return text
            
#------------------------------------------------------------------------
#
# WebReport
#
#------------------------------------------------------------------------
class WebReport(Report.Report):
    def __init__(self,database,person,options_class):
        """
        Creates WebReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter
        od
        NWEBimg
        NWEBrestrictinfo
        NWEBincpriv
        NWEBnotxtsi
        NWEBlnktoalphabet
        NWEBsplita
        NWEBplaceidx
        NWEBshorttree
        NWEBidxcol
        NWEBimagedir
        NWEBincid
        NWEBidurl
        NWEBlinktidx
        NWEBext
        NWEBencoding
        NWEBtreed
        NWEBidxt
        NWEBidxbirth
        NWEBintronote
        NWEBhomenote
        NWEBnoid
        yearso
        """
        self.database = database
        self.start_person = person
        self.options_class = options_class

        filter_num = options_class.get_filter_number()
        filters = options_class.get_report_filters(person)
        filters.extend(GenericFilter.CustomFilters.get_filters())
        self.filter = filters[filter_num]

        self.target_path = options_class.handler.options_dict['NWEBod']
        self.ext = options_class.handler.options_dict['NWEBext']
        self.encoding = options_class.handler.options_dict['NWEBencoding']
        self.id_link = options_class.handler.options_dict['NWEBlinktidx']
        self.photos = options_class.handler.options_dict['NWEBimg']
        self.restrict = options_class.handler.options_dict['NWEBrestrictinfo']
        self.private = options_class.handler.options_dict['NWEBincpriv']
        self.noid = options_class.handler.options_dict['NWEBnoid']
        self.srccomments = options_class.handler.options_dict['NWEBcmtxtsi']
        self.image_dir = options_class.handler.options_dict['NWEBimagedir']
        self.title = options_class.handler.options_dict['NWEBtitle']
        self.separate_alpha = options_class.handler.options_dict['NWEBsplita']
        self.depth = options_class.handler.options_dict['NWEBtreed']
        self.sort = Sort.Sort(self.database)
        self.inc_contact = options_class.handler.options_dict['NWEBcontact']
        self.inc_download = options_class.handler.options_dict['NWEBdownload']
        self.use_archive = options_class.handler.options_dict['NWEBarchive']

    def get_progressbar_data(self):
        return (_("Generate HTML reports - GRAMPS"),
                '<span size="larger" weight="bold">%s</span>' %
                _("Creating Web Pages"))

    def write_report(self):
        if not self.use_archive:
            dir_name = self.target_path
            if dir_name == None:
                dir_name = os.getcwd()
            elif not os.path.isdir(dir_name):
                parent_dir = os.path.dirname(dir_name)
                if not os.path.isdir(parent_dir):
                    ErrorDialog(_("Neither %s nor %s are directories") % \
                                (dir_name,parent_dir))
                    return
                else:
                    try:
                        os.mkdir(dir_name)
                    except IOError, value:
                        ErrorDialog(_("Could not create the directory: %s") % \
                                    dir_name + "\n" + value[1])
                        return
                    except:
                        ErrorDialog(_("Could not create the directory: %s") % \
                                    dir_name)
                        return

            if self.image_dir:
                image_dir_name = os.path.join(dir_name, self.image_dir)
            else:
                image_dir_name = dir_name
            if not os.path.isdir(image_dir_name) and self.photos != 0:
                try:
                    os.mkdir(image_dir_name)
                except IOError, value:
                    ErrorDialog(_("Could not create the directory: %s") % \
                                image_dir_name + "\n" + value[1])
                    return
                except:
                    ErrorDialog(_("Could not create the directory: %s") % \
                                image_dir_name)
                    return

        ind_list = self.database.get_person_handles(sort_handles=False)
        ind_list = self.filter.apply(self.database,ind_list)
        progress_steps = len(ind_list)
        if len(ind_list) > 1:
            progress_steps = progress_steps+1
        progress_steps = progress_steps+1
        self.progress_bar_setup(float(progress_steps))

        if self.use_archive:
            import TarFile
            archive = TarFile.TarFile(self.target_path)
        else:
            archive = None

        self.write_css(archive)

        HomePage(self.database, self.title, self.options_class, archive)
        if self.inc_contact:
            ContactPage(self.database, self.title, self.options_class, archive)
        if self.inc_download:
            DownloadPage(self.database, self.title, self.options_class, archive)
        
        IntroductionPage(self.database, self.title, self.options_class, archive)
        
        place_list = sets.Set()
        source_list = sets.Set()

        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)
            if not self.private:
                person = ReportUtils.sanitize_person(self.database,person)
                
            idoc = IndividualPage(self.database, person, self.title,
                                  ind_list, place_list, source_list,
                                  self.options_class, archive)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()
            
        if len(ind_list) > 1:
            IndividualListPage(self.database, self.title, ind_list,
                               self.options_class, archive)
            SurnameListPage(self.database, self.title, ind_list,
                            self.options_class, archive)
            self.progress_bar_step()
            while gtk.events_pending():
                gtk.main_iteration()

        PlaceListPage(self.database, self.title, place_list,
                      source_list,self.options_class, archive)
        
        for place in place_list:
            PlacePage(self.database, self.title, place, source_list,
                      self.options_class, archive)
            
        SourcesPage(self.database,self.title, source_list, self.options_class,
                    archive)
        if archive:
            archive.close()
        self.progress_bar_done()

    def write_css(self,archive):
        if archive:
            f = StringIO()
            f.write('\n'.join(_css))
            archive.add_file(_NARRATIVE,time.time(),f)
            f.close()
        else:
            f = open(os.path.join(self.target_path,_NARRATIVE), "w")
            f.write('\n'.join(_css))
            f.close()
                 
    def add_styles(self,doc):
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,database,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)
        self.db = database
        
    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'NWEBarchive'       : 0,
            'NWEBod'            : './',
            'NWEBimg'           : 2,
            'NWEBrestrictinfo'  : 0,
            'NWEBincpriv'       : 0,
            'NWEBnoid'          : 0,
            'NWEBcmtxtsi'       : 0, 
            'NWEBlnktoalphabet' : 0, 
            'NWEBsplita'        : 0, 
            'NWEBcontact'       : 0, 
            'NWEBdownload'      : 0, 
            'NWEBshorttree'     : 1,
            'NWEBimagedir'      : 'images', 
            'NWEBtitle'         : _('My Family Tree'), 
            'NWEBincid'         : 0,
            'NWEBidurl'         : '',
            'NWEBlinktidx'      : 1,
            'NWEBext'           : 'html',
            'NWEBencoding'      : 'utf-8',
            'NWEBtreed'         : 3,
            'NWEBidxt'          : '',
            'NWEBintronote'     : '',
            'NWEBhomenote'      : '',
            'NWEBidxbirth'      : 0,
            'NWEBplaceidx'      : 0,
            'NWEByearso'        : 1,
        }

        self.options_help = {
        }

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'filter'    : 0,
        }

    def get_report_filters(self,person):
        """Set up the list of possible content filters."""
        if person:
            name = person.get_primary_name().get_name()
            gramps_id = person.get_gramps_id()
        else:
            name = 'PERSON'
            gramps_is = ''

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        des = GenericFilter.GenericFilter()
        des.set_name(_("Descendants of %s") % name)
        des.add_rule(GenericFilter.IsDescendantOf([gramps_id,1]))

        df = GenericFilter.GenericFilter()
        df.set_name(_("Descendant Families of %s") % name)
        df.add_rule(GenericFilter.IsDescendantFamilyOf([gramps_id]))

        ans = GenericFilter.GenericFilter()
        ans.set_name(_("Ancestors of %s") % name)
        ans.add_rule(GenericFilter.IsAncestorOf([gramps_id,1]))

        com = GenericFilter.GenericFilter()
        com.set_name(_("People with common ancestor with %s") % name)
        com.add_rule(GenericFilter.HasCommonAncestorWith([gramps_id]))

        return [all,des,df,ans,com]

    def add_user_options(self,dialog):
        priv_msg = _("Do not include records marked private")
        restrict_msg = _("Restrict information on living people")
        no_img_msg = _("Do not use images")
        no_limg_msg = _("Do not use images for living people")
        no_com_msg = _("Do not include comments and text in source information")
        imgdir_msg = _("Image subdirectory")
        title_msg = _("Web site title")
        ext_msg = _("File extension")
        sep_alpha_msg = _("Split alphabetical sections to separate pages")
        tree_msg = _("Include short ancestor tree")
        contact_msg = _("Include publisher contact page")
        download_msg = _("Include download page")

        self.no_private = gtk.CheckButton(priv_msg)
        self.no_private.set_active(not self.options_dict['NWEBincpriv'])

        self.noid = gtk.CheckButton(_('Suppress GRAMPS ID'))
        self.noid.set_active(self.options_dict['NWEBnoid'])

        self.restrict_living = gtk.CheckButton(restrict_msg)
        self.restrict_living.set_active(self.options_dict['NWEBrestrictinfo'])

        self.inc_contact = gtk.CheckButton(contact_msg)
        self.inc_contact.set_active(self.options_dict['NWEBcontact'])

        self.inc_download = gtk.CheckButton(download_msg)
        self.inc_download.set_active(self.options_dict['NWEBdownload'])

        # FIXME: document this:
        # 0 -- no images of any kind
        # 1 -- no living images, but some images
        # 2 -- any images
        images = self.options_dict['NWEBimg']
        self.no_images = gtk.CheckButton(no_img_msg)
        self.no_images.set_active(not images)

        self.no_living_images = gtk.CheckButton(no_limg_msg)
        self.no_living_images.set_sensitive(not images)
        self.no_living_images.set_active(images in (0,1))

        self.no_comments = gtk.CheckButton(no_com_msg)
        self.no_comments.set_active(not self.options_dict['NWEBcmtxtsi'])

        self.imgdir = gtk.Entry()
        self.imgdir.set_text(self.options_dict['NWEBimagedir'])

        self.intro_note = gtk.Entry()
        self.intro_note.set_text(self.options_dict['NWEBintronote'])

        self.title = gtk.Entry()
        self.title.set_text(self.options_dict['NWEBtitle'])

        self.linkpath = gtk.Entry()
        self.linkpath.set_sensitive(self.options_dict['NWEBincid'])
        self.linkpath.set_text(self.options_dict['NWEBidurl'])

        self.ext = gtk.combo_box_new_text()
        self.ext_options = ['.html','.htm','.shtml','.php','.php3','.cgi']
        for text in self.ext_options:
            self.ext.append_text(text)

        def_ext = "." + self.options_dict['NWEBext']
        self.ext.set_active(self.ext_options.index(def_ext))

        cset_node = None
        cset = self.options_dict['NWEBencoding']

        store = gtk.ListStore(str,str)
        for data in _character_sets:
            if data[1] == cset:
                cset_node = store.append(row=data)
            else:
                store.append(row=data)
        self.encoding = GrampsNoteComboBox(store,cset_node)

        dialog.add_option(title_msg,self.title)
        dialog.add_option(imgdir_msg,self.imgdir)
        dialog.add_option(ext_msg,self.ext)
        dialog.add_option(_('Character set encoding'),self.encoding)

        title = _("Page Generation")

        cursor = self.db.get_media_cursor()
        media_list = [['',None]]
        data = cursor.first()
        while data:
            (handle, value) = data
            media_list.append([value[4],handle])
            data = cursor.next()
        cursor.close()
        media_list.sort()

        home_node = None
        home_note = self.options_dict['NWEBhomenote']

        store = gtk.ListStore(str,str)
        for data in media_list:
            if data[1] == home_note:
                home_node = store.append(row=data)
            else:
                store.append(row=data)
        self.home_note = GrampsNoteComboBox(store,home_node)

        dialog.add_frame_option(title,_('Home Media/Note ID'),
                                self.home_note)
        dialog.add_frame_option(title,_('Introduction Media/Note ID'),
                                self.intro_note)
        dialog.add_frame_option(title,None,self.inc_contact)
        dialog.add_frame_option(title,None,self.inc_download)
        dialog.add_frame_option(title,None,self.noid)

        title = _("Privacy")
        dialog.add_frame_option(title,None,self.no_private)
        dialog.add_frame_option(title,None,self.restrict_living)
        dialog.add_frame_option(title,None,self.no_images)
        dialog.add_frame_option(title,None,self.no_living_images)
        dialog.add_frame_option(title,None,self.no_comments)
        self.no_images.connect('toggled',self.on_nophotos_toggled)

    def parse_user_options(self,dialog):
        """Parse the privacy options frame of the dialog.  Save the
        user selected choices for later use."""
        
        self.options_dict['NWEBrestrictinfo'] = int(self.restrict_living.get_active())
        self.options_dict['NWEBincpriv'] = int(not self.no_private.get_active())
        self.options_dict['NWEBnoid'] = int(self.noid.get_active())
        self.options_dict['NWEBcontact'] = int(self.inc_contact.get_active())
        self.options_dict['NWEBdownload'] = int(self.inc_download.get_active())
        self.options_dict['NWEBimagedir'] = unicode(self.imgdir.get_text())
        self.options_dict['NWEBtitle'] = unicode(self.title.get_text())
        self.options_dict['NWEBintronote'] = unicode(self.intro_note.get_text())
        self.options_dict['NWEBhomenote'] = unicode(self.home_note.get_handle())

        index = self.ext.get_active()
        if index >= 0:
            html_ext = self.ext_options[index]
        else:
            html_ext = "html"
        if html_ext[0] == '.':
            html_ext = html_ext[1:]
        self.options_dict['NWEBext'] = html_ext

        self.options_dict['NWEBencoding'] = self.encoding.get_handle()

        self.options_dict['NWEBidurl'] = unicode(self.linkpath.get_text().strip())

        self.options_dict['NWEBcmtxtsi'] = int(not self.no_comments.get_active())
        if self.no_images.get_active():
            photos = 0
        elif self.no_living_images.get_active():
            photos = 1
        else:
            photos = 2
        self.options_dict['NWEBimg'] = photos
        self.options_dict['NWEBod'] = dialog.target_path

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def show_link(self,obj):
        self.linkpath.set_sensitive(obj.get_active())

    def on_nophotos_toggled(self,obj):
        """Keep the 'restrict photos' checkbox in line with the 'no
        photos' checkbox.  If there are no photos included, it makes
        no sense to worry about restricting which photos are included,
        now does it?"""
        self.no_living_images.set_sensitive(not obj.get_active())

    def make_default_style(self,default_style):
        """Make the default output style for the Web Pages Report."""
        pass

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportDialog(Report.ReportDialog):

    def __init__(self,database,person):
        self.database = database 
        self.person = person
        name = "navwebpage"
        translated_name = _("Generate Web Site")
        self.options_class = WebReportOptions(name,database)
        self.category = const.CATEGORY_WEB
        Report.ReportDialog.__init__(self,database,person,self.options_class,
                                    name,translated_name)
        self.style_name = None

        response = self.window.run()
        if response == gtk.RESPONSE_OK:
            try:
                self.make_report()
            except (IOError,OSError),msg:
                ErrorDialog(str(msg))
        self.window.destroy()

    def setup_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def parse_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def parse_html_frame(self):
        self.options_class.handler.options_dict['NWEBarchive'] = self.archive.get_active()
    
    def parse_paper_frame(self):
        pass
    
    def setup_html_frame(self):
        self.html_table = gtk.Table(3,3)
        self.html_table.set_col_spacings(12)
        self.html_table.set_row_spacings(6)
        self.html_table.set_border_width(0)
        html_label = gtk.Label("<b>%s</b>" % _("HTML Options"))
        html_label.set_alignment(0.0,0.5)
        html_label.set_use_markup(True)
        self.html_table.attach(html_label, 0, 3, 0, 1, gtk.FILL)

        label = gtk.Label(_("HTML Options"))
        self.output_notebook.append_page(self.html_table,label)

        self.archive = gtk.CheckButton(_('Store web pages in .tar.gz archive'))
        self.archive.set_alignment(0.0,0.5)
        self.archive.connect('toggled',self.archive_toggle)
        self.html_table.attach(self.archive, 1, 2, 1, 2, gtk.SHRINK|gtk.FILL)

    def archive_toggle(self,obj):
        if obj.get_active():
            self.target_fileentry.set_directory_entry(False)
            self.doc_label.set_label("%s:" % _("Filename"))
        else:
            self.target_fileentry.set_directory_entry(True)
            self.doc_label.set_label("%s:" % _("Directory"))

    def setup_paper_frame(self):
        pass

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Generate Web Site"),_("Web Page"))

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Target Directory")

    def get_target_is_directory(self):
        """This report creates a directory full of files, not a single file."""
        return 1
    
    def get_default_directory(self):
        """Get the name of the directory to which the target dialog
        box should default.  This value can be set in the preferences
        panel."""
        return self.options_class.handler.options_dict['NWEBod']    

    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass

    def setup_format_frame(self):
        """Do nothing, since we don't want a format frame (NWEB only)"""
        pass
    
    def setup_post_process(self):
        """The format frame is not used in this dialog.  Hide it, and
        set the output notebook to always display the html template
        page."""
        self.output_notebook.set_current_page(1)

    def parse_format_frame(self):
        """The format frame is not used in this dialog."""
        pass
    
    def make_report(self):
        """Create the object that will produce the web pages."""

        try:
            MyReport = WebReport(self.database,self.person,
                                 self.options_class)
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)


def sort_people(db,handle_list):
    import sets

    flist = sets.Set(handle_list)

    sname_sub = {}
    sortnames = {}
    cursor = db.get_person_cursor()
    node = cursor.first()
    while node:
        if node[0] in flist:
            primary_name = node[1][_NAME_COL]
            if primary_name.group_as:
                surname = primary_name.group_as
            else:
                surname = db.get_name_group_mapping(primary_name.surname)
            sortnames[node[0]] = primary_name.sname
            if sname_sub.has_key(surname):
                sname_sub[surname].append(node[0])
            else:
                sname_sub[surname] = [node[0]]
        node = cursor.next()
    cursor.close()

    sorted_lists = []
    temp_list = sname_sub.keys()
    temp_list.sort(locale.strcoll)
    for name in temp_list:
        slist = map(lambda x: (sortnames[x],x),sname_sub[name])
        slist.sort(lambda x,y: locale.strcoll(x[0],y[0]))
        entries = map(lambda x: x[1], slist)
        sorted_lists.append((name,entries))
    return sorted_lists

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def cl_report(database,name,category,options_str_dict):

    clr = Report.CommandLineReport(database,name,category,WebReportOptions,options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    try:
        MyReport = WebReport(database,clr.person,clr.option_class)
        MyReport.write_report()
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# Empty class to keep the BaseDoc-targeted format happy
#
#------------------------------------------------------------------------
class EmptyDoc:
    def __init__(self,styles,type,template,orientation,source=None):
        pass

    def init(self):
        pass

#-------------------------------------------------------------------------
#
# GrampsNoteComboBox
#
#-------------------------------------------------------------------------
class GrampsNoteComboBox(gtk.ComboBox):
    """
    Derived from the ComboBox, this widget provides handling of Report
    Styles.
    """

    def __init__(self,model=None,node=None):
        """
        Initializes the combobox, building the display column.
        """
        gtk.ComboBox.__init__(self,model)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        if node:
            self.set_active_iter(node)
        self.local_store = model

    def get_handle(self):
        """
        Returns the selected key (style sheet name).

        @returns: Returns the name of the selected style sheet
        @rtype: str
        """
        active = self.get_active_iter()
        handle = None
        if active:
            handle = self.local_store.get_value(active,1)
        return handle

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_report
register_report(
    name = 'navwebpage',
    category = const.CATEGORY_WEB,
    report_class = WebReportDialog,
    options_class = cl_report,
    modes = Report.MODE_GUI | Report.MODE_CLI,
    translated_name = _("Narrative Web Site"),
    status=(_("Beta")),
    description=_("Generates web (HTML) pages for individuals, or a set of individuals."),
    )
