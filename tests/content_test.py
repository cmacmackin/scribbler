#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  notebook_test.py
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
Unit tests for the ScribblerContent class
"""

import os.path
import shutil
from tempfile import mkdtemp
from filecmp import cmp
from copy import copy
from collections import namedtuple

from scribbler.notebook import Notebook
from scribbler.content  import ScribblerContent
from scribbler.errors import ScribblerError

from mock import MagicMock, patch
from nose.tools import *
import yaml

location = 'test_notebook'
note = None
page = None

def setup_module():
    """
    Create a notebook and directory tree on which to perform tests.
    """
    global note
    global page
    NB = namedtuple('Notebook', ['PDF_DIR', 'HTML_DIR', 'NOTE_DIR',
                                 'APPE_DIR', 'location',])
    nb = NB(Notebook.PDF_DIR, Notebook.HTML_DIR, Notebook.NOTE_DIR,
            Notebook.APPE_DIR, location)
    with patch('scribbler.content.ScribblerContent.update') as p:
        note = ScribblerContent('Monday', '2015-10-19', 
                                os.path.join(nb.NOTE_DIR, '2015-10-19-monday.md'), nb)
        assert note.name == 'Monday'
        assert note.date == '2015-10-19'
        assert note.src_path == os.path.join(nb.NOTE_DIR, '2015-10-19-monday.md')
        assert note.notebook == nb
        assert note.markup == 'md'
        assert note.slug == '2015-10-19-monday'
        p.assert_called_with()
    with patch('scribbler.content.ScribblerContent.update') as p:
        page = ScribblerContent('Test Page 1', '????-??-??',
                                os.path.join(nb.APPE_DIR, 'page1.md'), nb)

def teardown_module():
    """
    Remove directory tree in which tests were performed.
    """

def setup_null():
    pass

@raises(ScribblerError)
def extension_test():
    """
    Check that unrecognized markup extensions cause a failure.
    """
    obj = ScribblerContent('fails', '2015-10-21', 'notes/fails.pdf', None)

def pdf_path_test():
    """
    Ensures that ScribblerContent._pdf_path() returns appropriate value.
    """
    assert note._pdf_path() == os.path.join(Notebook.PDF_DIR, '2015-10-19-monday.pdf')

def html_path_test():
    """
    Ensures that ScribblerContent._html_path() returns appropriate value.
    """
    assert note._html_path() == os.path.join(Notebook.HTML_DIR, 'notes', '2015-10-19-monday.html')
    print page._html_path(), os.path.join(Notebook.HTML_DIR, 'pages', 'page1.html')
    assert page._html_path() == os.path.join(Notebook.HTML_DIR, 'pages', 'page1.html')

def mock_html_path(self):
    return '../test.html'

def mock_pdf_path(self):
    return '../test.pdf'

def teardown_update():
    try: os.remove(mock_html_path(1)[1:])
    except: pass
    try: os.remove(mock_pdf_path(1)[1:])    
    except: pass
    try: del note.html_path
    except: pass
    try: del note.pdf_path
    except: pass
    try: del note.pdf_date
    except: pass
    try: del note.src_date
    except: pass
    
@patch('scribbler.content.ScribblerContent._html_path', mock_html_path)
@patch('scribbler.content.ScribblerContent._pdf_path', mock_pdf_path)
@with_setup(setup_null, teardown_update)
def update_test():
    """
    Checks that ScribblerContent.update() gets the correcct information.
    """
    srcm = os.path.getmtime(os.path.join(note.notebook.location, note.src_path))
    note.update()
    assert note.html_path == None
    assert note.pdf_path == None
    assert note.pdf_date == 0
    assert note.src_date == srcm
    shutil.copy(os.path.join(note.notebook.location, note.src_path), mock_html_path(1)[1:])
    shutil.copy(os.path.join(note.notebook.location, note.src_path), mock_pdf_path(1)[1:])
    note.update()
    assert note.html_path == mock_html_path(1)
    assert note.pdf_path == mock_pdf_path(1)
    assert note.src_date == srcm
    assert note.pdf_date == os.path.getmtime(mock_pdf_path(1)[1:])

def setup_make_pdf():
    shutil.copy('to-pdf-test.html', mock_html_path(1)[1:])
    note.html_path = mock_html_path(1)
    
def teardown_make_pdf():
    teardown_update()

@patch('scribbler.content.ScribblerContent._pdf_path', mock_pdf_path)
@with_setup(setup_make_pdf, teardown_make_pdf)
def make_pdf_test():
    """
    Tests that ScribblerContent.make_pdf() produces a PDF in the correct location.
    """
    note.make_pdf()
    assert os.path.isfile(mock_pdf_path(1)[1:])
