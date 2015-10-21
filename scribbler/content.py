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
Contains class representing notes and appendices.
"""

import os

import pdfkit

from .errors import ScribblerError

class ScribblerContent(object):
    """
    Class representing Note and Appendix objects. Must pass the name of
    the note/appendix, the date it is for, the path to its source file,
    relative to notebook's notes directory, and the notebook object which
    contains it.
    """
    def __init__(self, name, date, src_path, notebook):
        self.notebook = notebook
        self.name = name
        self.date = date
        basename = os.path.basename(src_path)
        for ext in ['md', 'rst', 'html']:
            if basename.endswith(ext):
                self.markup = ext
                self.slug = basename[:len(basename)-len(ext)-1]
                break
        else:
            raise ScribblerError("Unrecognized extension for file '{}'".format(basename))
        self.src_path = src_path
        self.update()
    
    def _pdf_path(self):
        """
        Returns the path where a PDF file is expected to be, relative to
        the notebook root.
        """
        return os.path.join(self.notebook.PDF_DIR, self.slug + '.pdf')
    
    def _html_path(self):
        """
        Returns the path where an HTML file is expected to be, relative to
        the notebook root.
        """
        if os.path.basename(os.path.dirname(self.src_path)) == self.notebook.NOTE_DIR:
            return os.path.join(self.notebook.HTML_DIR, self.notebook.NOTE_DIR, self.slug + '.html')
        else:
            return os.path.join(self.notebook.HTML_DIR, 'pages', self.slug + '.html')
    
    def update(self):
        """
        Updates information about the content.
        """
        if not os.path.isfile(os.path.join(self.notebook.location, self.src_path)):
            raise ScribblerError("Note with path '{}' does not exist".format(self.src_path))
        self.src_date = os.path.getmtime(os.path.join(self.notebook.location,
                                         self.src_path))
        if os.path.isfile(os.path.join(self.notebook.location, self._html_path())):
            self.html_path = self._html_path()
        else:
            self.html_path = None
        if os.path.isfile(os.path.join(self.notebook.location, self._pdf_path())):
            self.pdf_path = self._pdf_path()
            self.pdf_date = os.path.getmtime(os.path.join(self.notebook.location,
                                             self.pdf_path))
        else:
            self.pdf_path = None
            self.pdf_date = 0
        
    def make_pdf(self):
        """
        Produces a PDF version of the content from its HTML version, if
        it requires updating or does not already exist.
        """
        print self._html_path()
        src = os.path.join(self.notebook.location, self.html_path)
        dest = os.path.join(self.notebook.location, self._pdf_path())
        pdfkit.from_file(src, dest)


#~ class IndexPage(object):
    #~ """
    #~ Represents the HTML index page (home page).
    #~ """
    #~ 
    #~ def __init__(self):
        #~ self.notebook = None
        #~ self.html_path = ''
        #~ self.pdf_path = ''
    #~ 
    #~ def make_pdf(self):
        #~ """
        #~ Produces a PDF version of the HTML index page (containing
        #~ information equivalent to a title page and an introducction)
        #~ if one does not exist or needs to be updated.
        #~ """
        #~ pass
        
