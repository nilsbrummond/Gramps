# -*- coding: utf-8 -*-
#!/usr/bin/env python

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

# ***********************************************
# Python Modules
# ***********************************************
import os
import glob, shutil
import codecs

#------------------------------------------------
#        Distutils/ Distutils2 modules
#------------------------------------------------
from distutils2 import logger
from distutils2.util import find_packages

const_file_in = os.path.join('gramps', 'const.py.in')
const_file = os.path.join('gramps', 'const.py')
if (os.path.exists(const_file_in) and not os.path.exists(const_file)):
    shutil.copy(const_file_in, const_file)
from gramps.const import PROGRAM_NAME, VERSION, URL_HOMEPAGE
#------------------------------------------------
#        Constants
#------------------------------------------------
_FILENAME = 'setup.cfg'

class CreateSetup(object):
    def __init__(self):
        self.classifiers = set()
        self.data = {'name': '',
                     'version': VERSION,
                     'Home-page' : '',
                     'download-url' : '',
                     'author' : '', 
                     'author_email' : '',
                     'maintainter' : '',
                     'maintainer_email' : '',
                     'classifier': self.classifiers,
                     'keywords' : [],
                     'summary' : '',
                     'license' : '',
                     'description' : '',
                     'long-description' : [],
                     'packages': [],
                     'package_data' : dict(),
                     'modules': [],
                     'platform': [],
                     'resources': [],
                     'extra_files': [],
                     'scripts': [],
                     }

        self.data['name'] = PROGRAM_NAME.lower()

        self.data['version'] = VERSION

        self.data['Home-page'] = URL_HOMEPAGE

        self.data['download-url'] = 'http://gramps-project.org/download/'

        self.data['author'] = 'Donald N. Allingham'

        self.data['author_email'] = 'don@gramps-project.org'

        self.data['maintainer'] = 'Gramps Development Team'

        self.data['maintainer_email'] = 'benny.malengier@gmail.com'

        self.data['description'] = 'Gramps (Genealogical Research and Analysis Management Programming System)'

        self.data['long_description'] = '''gramps (Genealogical Research and Analysis Management Programming
        System) is a GNOME based genealogy program supporting a Python based plugin system.
        '''

        self.data['license'] = 'GPL v2 or greater'

        self.data['platforms'] = [
            'Linux',
            'FreeBSD',
            'Mac OSX',
            'Windows']

        self.data['keywords'] = [
            'Genealogy',
            'Pedigree',
            'Ancestry',
            'Birth',
            'Marriage',
            'Death',
            'Family',
            'Family-tree',
            'GEDCOM']

        self.classifiers.update([
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Environment :: MacOS X',
            'Environment :: Plugins',
            'Environment :: Web Environment',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: GTK',
            'Framework :: Django',
             'Intended Audience :: Education',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Other Audience',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Natural Language :: Bulgarian',
            'Natural Language :: Catalan',
            'Natural Language :: Chinese (Simplified)',
            'Natural Language :: Croatian',
            'Natural Language :: Czech',
            'Natural Language :: Danish',
            'Natural Language :: Dutch',
            'Natural Language :: English',
            'Natural Language :: Esperanto',
            'Natural Language :: Finnish',
            'Natural Language :: French',
            'Natural Language :: German',
            'Natural Language :: Hebrew',
            'Natural Language :: Hungarian',
            'Natural Language :: Italian',
            'Natural Language :: Japanese',
            'Natural Language :: Norwegian',
            'Natural Language :: Polish',
            'Natural Language :: Portuguese (Brazilian)',
            'Natural Language :: Portuguese',
            'Natural Language :: Russian',
            'Natural Language :: Slovak',
            'Natural Language :: Slovenian',
            'Natural Language :: Spanish',
            'Natural Language :: Swedish',
            'Natural Language :: Ukranian',
            'Natural Language :: Vietnamese',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: Other OS',
            'Operating System :: POSIX :: BSD',
            'Operating System :: POSIX :: Linux',
            'Operating System :: POSIX :: SunOS/Solaris',
            'Operating System :: Unix',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Topic :: Database',
            'Topic :: Desktop Environment :: Gnome',
            'Topic :: Education',
            'Topic :: Multimedia',
            'Topic :: Other/Nonlisted Topic',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Sociology :: Genealogy'
        ])

        _packages = [
            'gramps',
            'gramps.cli',
            'gramps.DateHandler',
            'gramps.docgen',
            'gramps.DateHandler',
            'gramps.gen',
            'gramps.glade',
            'gramps.gui',
            'gramps.images',
            'gramps.plugins',
            'gramps.webapp']

        all_files = {
            'gramps' : [
                '*.py',
                'DateHandler/*.py',
                'docgen/*.py',
                'Filters/*.py',
                'Filters/*/*.py',
                'Filters/Rules/*/*.py',
                'GrampsLocale/*.py',
                'GrampsLogger/*.py',
                'Merge/*.py',
                'Simple/*.py',
                'TestPlan.txt',
                'test/*.py'],
            'gramps.cli': [
                '*.py',
                'plug/*.py'],
            'gramps.data': [
                '*.txt',
                '*.xml'],
            'gramps.gen': [
                '*.py',
                'db/*.py',
                'display/*.py',
                'lib/*.py',
                'mime/*.py',
                'plug/*.py',
                'plug/*/*.py',
                'proxy/*.py',
                'test/*.py',
                'utils/*.py'],
            'gramps.glade': [
                '*.glade',
                'glade/catalog/*.py',
                'catalog/*.xml'],
            'gramps.gui': [
                '*.py',
                'editors/*.py',
                'editors/*/*.py',
                'plug/*.py',
                'plug/*/*.py',
                'selectors/*.py',
                'views/*.py',
                'views/treemodels/*.py',
                'widgets/*.py'],
            'gramps.images': [
                '*/*.png',
                 '*/*.svg',
                '*.png',
                '*.jpg',
                '*.ico',
                 '*.gif'],
            'gramps.plugins': [
                '*.py',
                '*/*.py',
                'lib/*.xml',
                'lib/maps/*.py',
                'webstuff/css/*.css',
                'webstuff/images/*.svg',
                'webstuff/images/*.png',
                'webstuff/images/*.gif',            
                '*.glade',
                '*/*.glade'],
                'gramps.webapp': [
                '*.py',
                'webstuff/css/*.css',
                'webstuff/images/*.svg',
                'webstuff/images/*.png',
                'webstuff/images/*.gif',
                'grampsdb/fixtures/initial_data.json',
                '*/*.py',
                'sqlite.db',
                'grampsdb/*.py',
                'fixtures/initial_data.json',
                'templatetags/*py'],
        }
        self.data['packages'] = find_packages()

        file_data = dict((section, list()) for section in _packages
                if section not in ['gramps.data', 'gramps.images', 'gramps.plugins'])

        extra_data = dict((section, list()) for section in _packages
               if section in ['gramps.data', 'gramps.images', 'gramps.plugins'])

        for section in all_files:
            directory = section
            if '.' in directory:
                directory = '/'.join(directory.split('.'))
            tmp_filenames = []
            for file_match in all_files[section]:
                tmp_filenames.append([glob.glob(os.path.join(directory, file_match))])
                if section in file_data:
                    file_data[section] = tmp_filenames
                else:
                    extra_data[section] = tmp_filenames
        #self.data['modules']     = file_data
        self.data['extra_files'] = [
            'debian/*',
            'docs/*',
            'docs/*/*',
            'help/*',
            'mac/*',
            'po/*',
            'po/*/*',
            'test/*',
            'test/*/*',
            'windows/*',
            'windows/*/*']

        self.data['scripts'] = ['gramps.sh']

        self.data['requires_dist'] = [
            'pygtk2',
            'pycairo',
            'pygobject2']

        self.data['resources'] = [
            'example/**/*.* = {purelib}/gramps',
            'gramps/glade/**/*.* = {purelib}',
            'gramps/images/**/*.* = {purelib}',
            'gramps/plugins/**/*.* = {purelib}',
            'data/ gramps.desktop = {data}/share/applications',
            'gramps/images/ gramps.png = {icon}',
            'data/ gramps.xml = {data}/share/mime/packages',
            'data/ gramps.mime = {data}/share/mime-info',
            'data/ gramps.keys = {data}/share/mime-info',
            'data/ *.png = {data}/share/icons/gnome/48x48/mimetypes',
            'data/ *.svg = {data}/share/icons/gnome/scalable/mimetypes',
            'data/man/ gramps.1.in = {man}/man1',
            'data/man/cs/ gramps.1.in = {man}/cs/man1',
            'data/man/fr/ gramps.1.in = {man}/fr/man1',
            'data/man/nl/ gramps.1.in = {man}/nl/man1',
            'data/man/pl/ gramps.1.in = {man}/pl/man1',
            'data/man/sv/ gramps.1.in = {man}/sv/man1',
            'COPYING = {doc}',
            'FAQ = {doc}',
            'INSTALL = {doc}',
            'NEWS = {doc}',
            'README = {doc}',
            'TODO = {doc}']

    def main(self):
        if os.path.exists(_FILENAME):
            if os.path.exists('%s.old' % _FILENAME):
                message = ("ERROR: %(name)s.old backup exists, please check "
                           "that current %(name)s is correct and remove "
                           "%(name)s.old" % {'name': _FILENAME})
                logger.error(message)
                return
            else:
                shutil.move(_FILENAME, '%s.old' % _FILENAME)

        try: 
            fp = codecs.open(_FILENAME, 'w', encoding='utf-8')
        except IOError:
            print "ERROR: Failed to open file."
            return
            
        fp.write(u'[metadata]\n')
        # TODO use metadata module instead of hard-coding field-specific
        # behavior here

        # simple string entries
        for name in ('name', 'version', 'summary', 'download_url'):
            fp.write(u'%s = %s\n' % (name, self.data.get(name, 'UNKNOWN')))

        # optional string entries
        if ('keywords' in self.data and self.data['keywords']):
            # XXX shoud use comma to separate, not space
            fp.write(u'keywords = %s\n' % ' '.join(self.data['keywords']))

        for name in ('Home-page', 'author', 'author_email',
                     'maintainer', 'maintainer_email', 'description-file'):
            if (name in self.data and self.data[name]):
               fp.write(u'%s = %s\n' % (name.decode('utf-8'),
                                        self.data[name].decode('utf-8')))

        if ('description' in self.data and self.data['description']):
            fp.write(
                     u'description = %s\n'
                     % u'\n       |'.join(self.data['description'].split('\n')))

        # multiple use string entries
        for name in ('platform', 'supported-platform', 'classifier',
                     'requires-dist', 'provides-dist', 'obsoletes-dist', 'requires-external'):
            if not(name in self.data and self.data[name]):
                continue
            fp.write(u'%s = ' % name)
            fp.write(u''.join('    %s\n' % val
                              for val in self.data[name]).lstrip())

        fp.write(u'\n[files]\n')

        for name in ('packages', 'modules', 'scripts', 'extra_files'):
            if not(name in self.data and self.data[name]):
                continue
            fp.write(u'%s = %s\n'
                     % (name, u'\n    '.join(self.data[name]).strip()))

        if self.data.get('package_data'):
            fp.write(u'package_data =\n')
            for pkg, spec in sorted(self.data['package_data'].items()):
                # put one spec per line, indented under the package name
                indent = u' ' * (len(pkg) + 7)
                spec = (u'\n' + indent).join(spec)
                fp.write(u'    %s = %s\n' % (pkg, spec))
            fp.write(u'\n')

        if self.data.get('resources'):
            fp.write(u'resources =\n')
            #for src, dest in self.data['resources']:
                #fp.write(u'    %s = %s\n' % (src, dest))
            for entry in self.data['resources']:
                fp.write(u'    %s\n' % entry)                
            fp.write(u'\n')

        fp.close()

if __name__ == "__main__":
    cs = CreateSetup()
    cs.main()
