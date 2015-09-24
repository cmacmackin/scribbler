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
from copy import copy
from datetime import date
from pickle import dump

import yaml

class Notebook(object):
    DEFAULT_SETTINGS = {
        'author': 'No Author',
        'notebook name': 'A Scribbler Notebook',
        'timezone': 'Etc/UCT',
        'language': 'en',
        'links': [],
        'email': '',
        'description': 'This provides a description of your notebook. Talk '
                       'about what\'s in it, maybe providing a summary. '
                       'You might also want to write a bit about the '
                       'author. Don\'t give any contact details about the '
                       'author here, though. Those are provided elsewhere.',
        'address': False,
        'street address': '',
        'city': '',
        'postal': '',
        'country': '',
        'plugins': [],
        'markdown extensions': [],
        'bibfile': '',
        'filetypes': []
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
        'postal': 'POSTAL',
        'country': 'COUNTRY',
        'plugins': 'PLUGINS',
        'markdown extensions': 'MD_EXTENSIONS',
        'bibfile': 'PUBLICATIONS_SRC',
    }
    PELICAN_PLUGINS = ['scribbler.render_math', 'scribbler.tipue_search',
                       'scribbler.neighbors', 'scribbler.pdf-img',
                       'scribbler.slugcollision','scribbler.pelican-cite',
                       'scribbler.figure-ref']
    MARKDOWN_PLUGINS = ['scribbler.figureAltCaption','superscript',
                        'markdown_checklist.extension','extra','subscript',
                        'scribbler.markdown.highlight','subscript',
                        'codehilite(css_class=highlight)','del_ins',
                        'MarkdownHighlight.highlight',
                        'markdown_include.include']
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
        'tar.gz': 'tarballs',
        'tar.bz': 'tarballs',
        'tar.bz2': 'tarballs',
        'tar.xz': 'tarballs',
        'tar': 'tarballs',
        'rar': 'tarballs',
        'zip': 'tarballs',
        'rtp': 'tarballs',
        'deb': 'tarballs',
        '*': 'attachments'
    }   
    DEFAULT_PELICAN_SETTINGS = {
        'DELETE_OUTPUT_DIRECTORY': True,
        'OUTPUT_PATH': 'html/',
        'PATH': 'content/',
        'PAGE_PATHS': 'appendices',
        'RELATIVE_URLS': True,
        'THEME': '',
        'DIRECT_TEMPLATES':  ['index', 'archives', 'tags', 'search'],
        'TYPOGRIFY': True,
        'DEFAULT_PAGINATION': 10,
        'DEFAULT_ORPHANS': 2,
        'PAGINATED_DIRECT_TEMPLATES': ('tag', 'archives', 'period_archives'),
        'YEAR': date.today().year,
        'AUTHOR_SAVE_AS': '',
        'CATEGORY_SAVE_AS': '',
        'ARTICLE_URL': '{date:%Y}/{date:%b}/{date:%d}/{slug}.html',
        'ARTICLE_SAVE_AS': '{date:%Y}/{date:%b}/{date:%d}/{slug}.html',	
        'MONTH_ARCHIVE_SAVE_AS': '{date:%Y}/{date:%b}/index.html',
        'YEAR_ARCHIVE_SAVE_AS': '{date:%Y}/index.html',
    }
    SETTINGS_FILE = 'notebook.yml'
    PELICANCONF_FILE = '.__pelicanconf__.py'
    
    """
    A class describing and managing a Scribbler notebook. 
    """
    
    def __init__(self, name, location):
        """
        If location already exists, then try to read notebook
        information from its contents. This may override name. 
        Otherwise, create basic contents for a notebook at location.
        """
        self.name = name
        self.location = os.path.abspath(location)
        self._settings = None
        self._pelican_settings = None
        self.articles = []
        self.appendices = []
        #~ self.output_path = os.path.join(location,'html')
        #~ self.content_path = os.path.join(location,'content')
    
    @property
    def settings(self):
        '''
        Takes the YAML file containing settings for this notebook and 
        returns a dictionary constructed by adjusting the  default
        settings with this information.
        '''
        if self._settings:
            return self._settings
        settings_file = open(os.path.join(self.location,self.SETTINGS_FILE),'r')
        file_settings = yaml.load(settings_file)
        settings = copy(self.DEFAULT_SETTINGS)
        settings.update(file_settings)
        for key, val in settings.iteritems():
            if key in self.DEFAULT_SETTINGS and isinstance(val,type(self.DEFAULT_SETTINGS[key])):
                raise TypeError('Key "{}" in settings of type {}'.format(key,type(val)).__name__)
        tmp = settings['filetypes']
        settings['filteypes'] = copy(self.FILETYPES)
        settings['filetypes'].extend(tmp)
        settings['markdown extensions'].extend(self.MARKDOWN_PLUGINS)
        settings['plugins'].extend(self.PELICAN_PLUGINS)
        self._settings = settings
        return settings
    
    @property
    def pelican_settings(self):
        '''
        Returns a dictionary with the settings to be provided for Pelican.
        '''
        if self._pelican_settings:
            return self._pelican_settings
        psettings = copy(self.DEFAULT_PELICAN_SETTINGS)
        psettings['OUTPUT_PATH'] = os.path.join(self.location,psettings['OUTPUT_PATH'])
        psettings['PATH'] = os.path.join(self.location,psettings['PATH'])
        for key, val in self.settings.iteritems():
            if key in self.PELICAN_MAPPING:
                psettings[self.PELICAN_MAPPING[key]] = self.settings[key]
        self._pelican_settings = psettings
        return psettings
    
    def make_pelicanconf(self):
        """
        Create .pelicanconf.py from the notebook settings.
        """
        pfile = open(os.path.join(self.location, self.PELICANCONF_FILE), 'w')
        pfile.write('#!/usr/bin/env python\n'
                    '# -*- coding: utf-8 -*- #\n'
                    'from __future__ import unicode_literals\n')
        for key, val in self.pelican_settings.iteritems():
            pfile.write('{} = {}\n'.format(key, repr(val)))
        pfile.close()
    
    def del_pelicanconf(self):
        if os.path.isfile(os.path.join(self.location, self.PELICANCONF_FILE)):
            os.remove(os.path.join(self.location, self.PELICANCONF_FILE))
            return True
        else:
            return False
    
    def copy_in(self, path, location=None):
        """
        Copy the file at the specified path into the notebook contents
        If location is specified, place it there. Otherwise, place in
        default location for that filetypes.
        """
        pass
    
    def link_in(self, path, location=None):
        """
        Create hard link in the notebook contents to the file at the 
        specified path. If location is specified, place link there.
        Otherwise, place in default locations for that filetype.
        """
        pass
    
    def symlink_in(self, paths, location=None):
        """
        Create symbolic link in the notebook contents to the file at the
        specified path. If location is specified, place link there.
        Otherwise, place in default locations for those filetypes.
        """
        pass
    
    def newnote(self, date, title):
        """
        Create a new note with the specified date and title.
        """
        pass
    
    def newpage(self, title):
        """
        Create a new page ("appendix") with the specified title.
        """
        pass
        
    def list_contents(self):
        """
        Return a list (format to be determined) detailing the notes,
        appendices, and possibly static content stored in the notebook's
        content directory.
        """
        pass
    
    def build(self):
        """
        Run Pelican to produce the HTML for this notebook. Then produce
        the PDF pages.
        """
        self.make_pelicanconf()
        subprocess.call(['pelican','-s',os.path.join(self.location,self.PELICANCONF_FILE)])
        self.del_pelicanconf()
        self.update()
        # TODO: add the code to produce PDFs
    
    def update(self):
        """
        Update the list of the content stored in this notebook.
        """
        pass
    
    def save(self, path):
        """
        Asks notebook to pickle itself and stores it in the specified path.
        """
        out = open(path,'w')
        dump(self, out)
        out.close()

