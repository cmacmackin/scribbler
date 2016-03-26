#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  notebook.py
#  
#  Copyright 2014 Christopher MacMackin <cmacmackin@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

"""
Contains a class for representing a Scribbler notebook.
"""

import os.path
import subprocess
import shutil
from copy import copy
from datetime import date, datetime
from pickle import dump, load
from glob import glob

from pelican.utils import slugify
import yaml
import pdfkit
from scribbler.PyPDF2 import PdfFileMerger

from .errors import ScribblerWarning, ScribblerError
from .content import ScribblerContent

class Notebook(object):
    """
    A class describing and managing a Scribbler notebook. 
    """
    CONTENT_DIR = '.__content__'
    SETTINGS_FILE = 'notebook.yml'
    BACKUP_FILE = '.__notebook__.pkl'
    PELICANCONF_FILE = '.__pelicanconf__.py'
    NOTE_DIR = 'notes'
    APPE_DIR = 'appendices'
    STATIC_DIR = 'files'
    HTML_DIR = 'html'
    PDF_DIR = 'pdf'
    MASTER_PDF = 'FullNotebook.pdf'
    DEFAULT_SETTINGS = {
        'author': 'No Author',
        'notebook name': 'A Scribbler Notebook',
        'timezone': 'Etc/UCT',
        'language': 'en',
        'links': [],
        'email': '',
        'description': '',
        'address': False,
        'street address' : '',
        'city': '',
        'region': '',
        'postal': '',
        'country': '',
        'plugins': [],
        'markdown extensions': [],
        'bibfile': '',
        'filetypes': {},
        'paper': 'Letter',
    }
    PELICAN_MAPPING = {
        'author': 'AUTHOR',
        'notebook name': 'SITENAME',
        'timezone': 'TIMEZONE',
        'language': 'DEFAULT_LANG',
        'links': 'LINKS',
        'email': 'EMAIL',
        'description': 'DESCRIPTION',
        'address': 'ADDRESS',
        'street address': 'STREET_ADDRESS',
        'city': 'CITY',
        'region': 'REGION',
        'postal': 'POSTAL',
        'country': 'COUNTRY',
        'plugins': 'PLUGINS',
        'markdown extensions': 'MD_EXTENSIONS',
        'bibfile': 'PUBLICATIONS_SRC',
    }
    NO_MAPPING = ['paper', 'filetypes']
    PELICAN_PLUGINS = ['scribbler.render_math', 'scribbler.tipue_search',
                       'scribbler.neighbors', 'scribbler.pdf-img',
                       'scribbler.slugcollision','scribbler.pelican-cite',
                       'scribbler.figure-ref']
    MARKDOWN_PLUGINS = ['scribbler.figureAltCaption','superscript',
                        'markdown_checklist.extension','extra',
                        'subscript','MarkdownHighlight.highlight',
                        'codehilite(css_class=highlight)','del_ins',
                        'markdown_include.include(base_path={})',
                        'scribbler.plantuml']
    FILETYPES = {
        'jpg': 'images',
        'jpeg': 'images',
        'png': 'images',
        'gif': 'images',
        'eps': 'images',
        'svg': 'images',
        'pdf': 'pdfs',
        'ps': 'pdfs',
        'dvi': 'pdfs',
        'tar.gz': 'archives',
        'tar.bz': 'archives',
        'tar.bz2': 'archives',
        'tar.xz': 'archives',
        'tar': 'archives',
        'rar': 'archives',
        'zip': 'archives',
        'rtp': 'archives',
        'deb': 'archives',
        '*': 'attachments'
    }   
    DEFAULT_PELICAN_SETTINGS = {
        'DELETE_OUTPUT_DIRECTORY': True,
        'OUTPUT_PATH': HTML_DIR,
        'PATH': CONTENT_DIR,
        'ARTICLE_PATHS': [NOTE_DIR],
        'PAGE_PATHS': [APPE_DIR],
        'STATIC_PATHS': [STATIC_DIR],
        'RELATIVE_URLS': True,
        'THEME': os.path.normpath(os.path.join(os.path.dirname(__file__), 'notebook-theme')),
        'DIRECT_TEMPLATES':  ['index', 'archives', 'tags', 'search'],
        'TYPOGRIFY': True,
        'DEFAULT_PAGINATION': 10,
        'DEFAULT_ORPHANS': 2,
        'PAGINATED_DIRECT_TEMPLATES': ('index', 'tag', 'archives', 'period_archives'),
        'YEAR': date.today().year,
        'AUTHOR_SAVE_AS': '',
        'CATEGORY_SAVE_AS': '',
        'ARTICLE_URL': NOTE_DIR + '/{slug}.html',
        'ARTICLE_SAVE_AS': NOTE_DIR + '/{slug}.html',	
        'SLUGIFY_SOURCE': 'basename',
        'FEED_ALL_ATOM': None,
        'CATEGORY_FEED_ATOM': None,
        'AUTHOR_FEED_ATOM': None,
        'AUTHOR_FEED_RSS': None,
        'SITEURL': 'http://www.null.org',
        'MATH_JAX': {'message_style': 'none'},
        #~ 'MONTH_ARCHIVE_SAVE_AS': '{date:%Y}/{date:%b}/index.html',
        #~ 'YEAR_ARCHIVE_SAVE_AS': '{date:%Y}/index.html',
    }
    PDF_SETTINGS = {
        #~ 'margin-top': '0.9in',
        #~ 'margin-right': '0.0in',
        #~ 'margin-bottom': '0.9in',
        #~ 'margin-left': '0.0in',
        'quiet': '',
        'print-media-type': '',
        'javascript-delay': '5000',
    }
    
    def __init__(self, name, location):
        """
        If location already exists, then try to read notebook
        information from its contents. This may override name. 
        Otherwise, create basic contents for a notebook at location.
        """
        subdirs = [os.path.join(location, d) for d in 
                    [Notebook.APPE_DIR, Notebook.HTML_DIR, Notebook.PDF_DIR,
                     Notebook.NOTE_DIR, Notebook.STATIC_DIR]
                  ]
        self.name = name
        self.location = os.path.abspath(location)
        self._settings = None
        self._pelican_settings = None
        self.notes = {}
        self.appendices = {}
        self.settings_mod_time = 0
        self.psettings_mod_time = 0
        for dirname in subdirs:
            try:
                os.mkdir(dirname)
            except:
                pass
        #~ self.output_path = os.path.join(location,'html')
        #~ self.content_path = os.path.join(location,'content')
    
    def __eq__(self, other):
        """
        Equality test, needed for unit testing.
        """
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False
    
    @property
    def settings(self):
        '''
        Takes the YAML file containing settings for this notebook and 
        returns a dictionary constructed by adjusting the  default
        settings with this information.
        '''
        yaml_time = os.path.getmtime(os.path.join(self.location,self.SETTINGS_FILE))
        if self._settings and yaml_time <= self.settings_mod_time:
            return self._settings
        settings_file = open(os.path.join(self.location,self.SETTINGS_FILE),'r')
        file_settings = yaml.load(settings_file)
        settings = copy(self.DEFAULT_SETTINGS)
        settings.update(file_settings)
        if isinstance(settings['description'], unicode):
            settings['description'] = str(settings['description'])
        for key, val in settings.iteritems():
            if key in self.DEFAULT_SETTINGS and not isinstance(val,type(self.DEFAULT_SETTINGS[key])):
                raise TypeError('Key "{}" in settings has value of type {}'.format(key,type(val).__name__))
        tmp = settings['filetypes']
        settings['filetypes'] = copy(self.FILETYPES)
        settings['filetypes'].update(tmp)
        settings['markdown extensions'].extend(self.MARKDOWN_PLUGINS)
        pplugins = copy(self.PELICAN_PLUGINS)
        pplugins[-1] = pplugins[-1].format(self.location)
        settings['plugins'] = pplugins + settings['plugins']
        settings['bibfile'] = os.path.join(self.location, settings['bibfile'])
        self._settings = settings
        self.settings_mod_time = yaml_time
        return settings
    
    @property
    def pelican_settings(self):
        '''
        Returns a dictionary with the settings to be provided for Pelican.
        '''
        self.settings # Called so that self.settings_mod_time will be updated
        if self._pelican_settings and self.settings_mod_time <= self.psettings_mod_time:
            return self._pelican_settings
        psettings = copy(self.DEFAULT_PELICAN_SETTINGS)
        psettings['OUTPUT_PATH'] = os.path.join(self.location,psettings['OUTPUT_PATH'])
        psettings['PATH'] = os.path.join(self.location,psettings['PATH'])
        for key, val in self.settings.iteritems():
            if key in self.PELICAN_MAPPING:
                psettings[self.PELICAN_MAPPING[key]] = self.settings[key]
            elif key not in self.NO_MAPPING:
                raise ScribblerWarning('Unrecognized setting: `{}`'.format(key))
        self._pelican_settings = psettings
        self.psettings_mod_time = self.settings_mod_time
        return psettings
    
    @property
    def pdf_settings(self):
        """
        Returns a dictionary with the settings to be handed to pdfkit.
        """
        settings = copy(self.PDF_SETTINGS)
        settings['page-size'] = self.settings['paper']
        return settings
    
    def make_pelicanconf(self):
        """
        Create .pelicanconf.py from the notebook settings.
        """
        pfile = open(os.path.join(self.location, self.PELICANCONF_FILE), 'w')
        pfile.write('#!/usr/bin/env python\n'
                    '# -*- coding: utf-8 -*- #\n'
                    '#from __future__ import unicode_literals\n')
        for key, val in self.pelican_settings.iteritems():
            pfile.write('{} = {}\n'.format(key, repr(val)))
        pfile.close()
    
    def del_pelicanconf(self):
        """
        Delete pelicanconf file if exists. Returns True if did exist,
        False otherwise.
        """
        if os.path.isfile(os.path.join(self.location, self.PELICANCONF_FILE)):
            os.remove(os.path.join(self.location, self.PELICANCONF_FILE))
            if os.path.isfile(os.path.join(self.location, self.PELICANCONF_FILE+'c')):
                os.remove(os.path.join(self.location, self.PELICANCONF_FILE+'c'))
            return True
        else:
            return False
    
    @staticmethod
    def mkdirs(path):
        """
        If they do not exist, creates all directories needed for PATH.
        """
        try:
            os.makedirs(os.path.dirname(path))
        except:
            pass
    
    def get_destination(self, path, location=None):
        """
        Returns the location in which to place the file.
        """
        # TODO: note that there may be corner cases I have not thought of or properly accounted for here
        if path.strip().endswith(os.path.sep): path = os.path.dirname(path)
        filename = os.path.basename(path)
        if isinstance(location, str):
            loc = location
            if os.path.isdir(os.path.join(self.location,self.STATIC_DIR,loc)):
                loc = os.path.join(loc, filename)
            if os.path.isdir(path):
                loc += os.path.sep
        else:
            for ext, dest in self.settings['filetypes'].iteritems():
                if ext != '*' and filename.endswith('.' + ext):
                    loc = dest
                    break
            else:
                try:
                    loc = self.settings['filetypes']['*']
                except KeyError:
                    raise ScribblerError('Could not find location for '
                                         'type of file ' + filename)
            loc = os.path.join(loc, filename)
        return os.path.join(self.location, self.STATIC_DIR, loc)
    
    def copy_in(self, path, location=None, overwrite=False):
        """
        Copy the file at the specified path into the notebook contents
        If location is specified, place it there. Otherwise, place in
        default location for that filetypes.
        """
        dest = self.get_destination(path, location)
        if not overwrite and (os.path.isfile(dest) or os.path.isdir(dest)):
            raise OSError("File already exists at '{}'".format(dest))
        elif overwrite and os.path.isdir(dest):
            if os.path.islink(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        self.mkdirs(dest)
        if os.path.isdir(path):
            shutil.copytree(path, dest)
        else:
            shutil.copy(path, dest)
    
    def link_in(self, path, location=None, overwrite=False):
        """
        Create hard link in the notebook contents to the file at the 
        specified path. If location is specified, place link there.
        Otherwise, place in default locations for that filetype.
        """
        if os.path.isdir(path):
            raise OSError("File '{}' is a directory".format(path))
        dest = self.get_destination(path, location)
        if os.path.isfile(dest):
            if overwrite:
                os.remove(dest)
            else:
                raise OSError("File already exists at '{}'".format(dest))
        self.mkdirs(dest)
        os.link(path, dest)

    def symlink_in(self, path, location=None, overwrite=False):
        """
        Create symbolic link in the notebook contents to the file at the
        specified path. If location is specified, place link there.
        Otherwise, place in default locations for those filetypes.
        """
        dest = self.get_destination(path, location)
        if not overwrite and (os.path.isfile(dest) or os.path.isdir(dest)):
            raise OSError("File already exists at '{}'".format(dest))
        elif overwrite and os.path.isfile(dest):
            os.remove(dest)
        elif overwrite and os.path.isdir(dest):
            if os.path.islink(dest):
                os.remove(dest)
            else:
                shutil.rmtree(dest)
        self.mkdirs(dest)
        if os.path.isabs(path):
            rpath = path
        else:
            if dest.endswith(os.path.sep):
                rpath = os.path.relpath(os.path.abspath(path), dest[:len(os.path.sep)])
            else:
                rpath = os.path.relpath(os.path.abspath(path), os.path.dirname(dest))
        os.symlink(rpath, dest)
    
    def newnote(self, date, title, markup='md'):
        """
        Create a new note with the specified date and title. Returns the
        path to that note.
        """
        MARKUP_OPTIONS = {
            'md': "Title: {0}\nDate: {1}\nTags: \n\n",
            'rst': "{0}\n###################\n\n:date: {1}\n:tags: \n\n",
            'html': "<html>\n\t<head>\n\t\t<title>{0}</title>\n\t\t"
                    "<meta name='date' content='{1}' />\n\t\t"
                    "<meta name='tags' content=' ' />\n\t</head>"
                    "\n\t<body>\n\t\t\n\t</body>\n</html>\n",
        }
        try:
            datetime.strptime(date, '%Y-%m-%d %H:%M')
        except:
            raise ScribblerError('Incorrectly formatted date; date format '
                             'should be YYYY-MM-DD HH:mm')
        name = date.split()[0] + '-' + slugify(title)
        for ext in MARKUP_OPTIONS:
            if os.path.isfile(os.path.join(self.location,self.NOTE_DIR,
                              name + '.' + ext)):
                raise ScribblerError('Date and name produce slug the '
                                     'same as existing file ' + name +
                                     '.' + ext)
        basename = name + '.' + markup
        path = os.path.join(self.location, self.NOTE_DIR, basename)
        out = open(path, 'w')
        try:
            out.write(MARKUP_OPTIONS[markup].format(title, date))
            out.close()
        except KeyError as e:
            out.close()
            os.remove(path)
            raise e
        self.notes[basename] = ScribblerContent(title, date[0:10], 
                                                os.path.join(self.NOTE_DIR, basename),
                                                self)
        self.save(os.path.join(self.location, self.BACKUP_FILE))
        return path
    
    def newpage(self, title, markup='md'):
        """
        Create a new page ("appendix") with the specified title. Returns
        the path to the page file.
        """
        MARKUP_OPTIONS = {
            'md': "Title: {0}\n\n",
            'rst': "{0}\n###################\n\n",
            'html': "<html>\n\t<head>\n\t\t<title>{0}</title>\n\t</head>"
                    "\n\t<body>\n\t\t\n\t</body>\n</html>\n",
        }
        name = slugify(title)
        for ext in MARKUP_OPTIONS:
            if os.path.isfile(os.path.join(self.location,self.APPE_DIR,
                              name + '.' + ext)):
                raise ScribblerError('Date and name produce slug the '
                                     'same as existing file ' + name +
                                     '.' + ext)
        basename = name + '.' + markup
        path = os.path.join(self.location, self.APPE_DIR, basename)
        out = open(path, 'w')
        try:
            out.write(MARKUP_OPTIONS[markup].format(title))
            out.close()
        except KeyError as e:
            out.close()
            os.remove(path)
            raise e
        self.appendices[basename] = ScribblerContent(title, '????-??-??', 
                                                     os.path.join(self.APPE_DIR, 
                                                     basename), self)
        self.save(os.path.join(self.location, self.BACKUP_FILE))
        return path
    
    def addnote(self, date, title, path, overwrite=False):
        """
        Add a record of a note in an existing file (PATH), not previously
        registered with Scribbler. Note has TITLE and DATE specified.
        """
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except:
            raise ScribblerError('Incorrectly formatted date; date format '
                             'should be YYYY-MM-DD')
        basename = os.path.relpath(os.path.abspath(path), os.path.join(self.location, self.NOTE_DIR))
        if basename in self.notes and not overwrite:
            raise ScribblerError('Note with file `{}` already exists.'.format(basename))
        self.notes[basename] = ScribblerContent(title, date,
                                    os.path.join(self.NOTE_DIR, basename), self)
        self.save(os.path.join(self.location, self.BACKUP_FILE))
        
    def addpage(self, title, path, overwrite=False):
        """
        Add a record of a page/appendix in an existing file (PATH), not
        previously registered with Scribbler. Has the specified TITLE.
        """
        basename = os.path.relpath(path, os.path.join(self.location, self.APPE_DIR))
        if basename in self.appendices and not overwrite:
            raise ScribblerError('Note with file `{}` already exists.'.format(basename))
        self.appendices[basename] = ScribblerContent(title, '????-??-??',
                                        os.path.join(self.APPE_DIR, basename), self)
        self.save(os.path.join(self.location, self.BACKUP_FILE))
        
    def list_contents(self):
        """
        Return a list (format to be determined) detailing the notes,
        appendices, and possibly static content stored in the notebook's
        content directory.
        """
        raise NotImplementedError() #TODO: Add this feature

    def build(self, debug=False):
        """
        Run Pelican to produce the HTML for this notebook. Then produce
        the PDF pages. Passes `--debug` flag to Pelican if DEBUG is true.
        """
        self.make_pelicanconf()
        content = os.path.join(self.location, self.CONTENT_DIR)
        if os.path.isdir(content): shutil.rmtree(content)
        os.mkdir(content)
        shutil.copytree(os.path.join(self.location, self.NOTE_DIR), 
                        os.path.join(content, self.NOTE_DIR))
        shutil.copytree(os.path.join(self.location, self.APPE_DIR),
                        os.path.join(content, self.APPE_DIR))
        shutil.copytree(os.path.join(self.location, self.STATIC_DIR),
                        os.path.join(content, self.STATIC_DIR))
        print('Producing HTML files...')
        call = ['pelican','-s',os.path.join(self.location,self.PELICANCONF_FILE)]
        if debug:
            call.append('--debug')
        subprocess.call(call)
        #~ self.del_pelicanconf()
        self.update()
        #~ shutil.rmtree(content)
        print('Producing PDF files...')
        if not os.path.isdir(os.path.join(self.location, self.PDF_DIR)):
            os.mkdir(os.path.join(self.location, self.PDF_DIR))
        master = PdfFileMerger(strict=False)
        master.addMetadata({u'/Title': self.settings['notebook name'],
                            u'/Author': self.settings['author']})
        src = os.path.join(self.location, self.HTML_DIR, 'index.html')
        dest = os.path.join(self.location, self.PDF_DIR, 'titlepage.pdf')
        pdfkit.from_file(src, dest, options=self.pdf_settings)
        master.append(dest)
        for note in sorted(self.notes.values(), key=lambda n: n.slug):
            if note.pdf_date < note.src_date:
                note.make_pdf()
                note.update()
            master.append(os.path.join(self.location, note.pdf_path),
                          note.date + ': ' + note.name)
        for appe in sorted(self.appendices.values(), key=lambda a: a.slug):
            if appe.pdf_date < appe.src_date:
                appe.make_pdf()
                appe.update()
            master.append(os.path.join(self.location, appe.pdf_path),
                          'Appendix: ' + appe.name)
        master.write(os.path.join(self.location, self.PDF_DIR, self.MASTER_PDF))
        print('Done.')
        self.update()

    def update(self):
        """
        Update the list of the content stored in this notebook.
        """
        notes = copy(self.notes)
        for root, dirs, files in os.walk(os.path.join(self.location, self.NOTE_DIR)):
            for f in files:
                if f in notes:
                    self.notes[f].update()
                    del notes[f]
                else:
                    if f.endswith('~') or f.startswith('.') or f.startswith('#'):
                        continue
                    path = os.path.join(os.path.relpath(root, self.location), f)
                    self.notes[f] = ScribblerContent('Unknown', '????-??-??',
                                                     path, self)
        for n in notes:
            del self.notes[n]
        appen = copy(self.appendices)
        for root, dirs, files in os.walk(os.path.join(self.location, self.APPE_DIR)):
            for f in files:
                if f in appen:
                    self.appendices[f].update()
                    del appen[f]
                else:
                    if f.endswith('~') or f.startswith('.') or f.startswith('#'):
                        continue
                    path = os.path.join(os.path.relpath(root, self.location), f)
                    self.appendices[f] = ScribblerContent('Unknown', '????-??-??',
                                                          path, self)
        for a in appen:
            del self.appendices[a]
        self.save(os.path.join(self.location, self.BACKUP_FILE))

    def save(self, path):
        """
        Asks notebook to pickle itself and stores it in the specified path.
        """
        out = open(path,'w')
        dump(self, out)
        out.close()


def create_notebook(name, location):
    """
    Looks to see if a notebook exists in this location. If so, loads
    and returns it. Otherwise, creates one there and then returns a
    corresponding object.
    """
    if os.path.isdir(location):
        if not os.path.isfile(os.path.join(location, Notebook.SETTINGS_FILE)):
            with open(os.path.join(location, Notebook.SETTINGS_FILE), 'w') as f:
                f.write("# Notebook configuration file\n")
                f.write("notebook name: {}".format(name))
        try:
            infile = open(os.path.join(location, Notebook.BACKUP_FILE), 'r')
            nb = load(infile)
            nb.location = os.path.abspath(location)
        except:
            nb = Notebook(name, location)
        nb.update()
    else:
        os.mkdir(location)
        with open(os.path.join(location, Notebook.SETTINGS_FILE), 'w') as f:
            f.write("# Notebook configuration file\n")
            f.write("notebook name: {}".format(name))
        nb = Notebook(name, location)
    nb.save(os.path.join(location, nb.BACKUP_FILE))
    return nb
