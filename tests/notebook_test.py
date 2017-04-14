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
Unit tests for the Notebook class
"""

import os.path
import shutil
from tempfile import mkdtemp
from filecmp import cmp
from copy import copy
from time import sleep
from pickle import load

from scribbler.notebook import *
from scribbler.content import *
from scribbler.errors import ScribblerError

from mock import MagicMock, patch
from nose.tools import *
import yaml

# Common variables to use for a test notebook
loc = None
nb = None

def setup_module():
    """
    Create a notebook and directory tree on which to perform tests.
    """
    global loc
    global nb
    loc = mkdtemp()
    nb = Notebook('Unit Testing', loc)
    assert nb.name == 'Unit Testing'
    if not loc.endswith(os.path.sep): loc += os.path.sep
    assert os.path.abspath(nb.location) == os.path.abspath(loc)
    os.makedirs(os.path.join(loc, Notebook.STATIC_DIR, 'example'))
    os.makedirs(os.path.join(loc, Notebook.STATIC_DIR, 'subdir'))

def teardown_module():
    """
    Remove directory tree in which tests were performed.
    """
    shutil.rmtree(loc)


def mock_scribbler_content(self, name, date, src_path, notebook):
    """
    Replace the constructor of a ScribblerContent object.
    """
    self.src_path = src_path

@property
def mock_settings(self):
    """
    Returns default Notebook settings without needing to import a YAML file.
    """
    settings = copy(self.DEFAULT_SETTINGS)
    settings['filetypes'] = copy(self.FILETYPES)
    settings['markdown extensions'] = self.MARKDOWN_PLUGINS
    settings['plugins'] = self.PELICAN_PLUGINS
    return settings

@property
@patch('scribbler.notebook.Notebook.settings', mock_settings)
def mock_psettings(self):
    '''
    Returns default Pelican settings without needing to import a YAML file.
    '''
    psettings = copy(self.DEFAULT_PELICAN_SETTINGS)
    psettings['OUTPUT_PATH'] = os.path.join(self.location,psettings['OUTPUT_PATH'])
    psettings['PATH'] = os.path.join(self.location,psettings['PATH'])
    for key, val in self.settings.iteritems():
        if key in self.PELICAN_MAPPING:
            psettings[self.PELICAN_MAPPING[key]] = self.settings[key]
        elif key not in self.NO_MAPPING:
            raise ScribblerWarning('Unrecognized setting: `{}`'.format(key))
    return psettings

def mock_save(self, path):
    """
    Replaces Notebook.save() with a stub which does nothing.
    """
    pass

def mock_update(self):
    """
    Replaces Notebook.update() with version that doesn't create/call content objects.
    """
    pass


def setup_null():
    pass

@patch('scribbler.notebook.Notebook.settings', mock_settings)
def get_destination_no_loc_test():
    """
    Tests Notebook.get_destination() method works with no location passed.
    """
    for ftype in nb.FILETYPES:
        if ftype == '*':
            name = 'unittest'
        else:
            name = 'unittest.' + ftype
        print ftype
        assert nb.get_destination(name) == os.path.join(loc, nb.STATIC_DIR, nb.FILETYPES[ftype], name)
        name = os.path.join('~/Pictures/stuff', name)
        assert nb.get_destination(name) == os.path.join(loc, nb.STATIC_DIR, nb.FILETYPES[ftype], os.path.basename(name))
        
@patch('scribbler.notebook.Notebook.settings', mock_settings)
def get_destination_loc_test():
    """
    Tests Notebook.get_destination() method works when location is passed.
    """
    assert nb.get_destination('copy_tests/test.pdf', '') == os.path.join(loc, nb.STATIC_DIR, 'test.pdf')
    assert nb.get_destination('copy_tests/test.pdf', 'test.pdf') == os.path.join(loc, nb.STATIC_DIR, 'test.pdf')
    assert nb.get_destination('copy_tests/test.pdf', 'pdfs/test.pdf') == os.path.join(loc, nb.STATIC_DIR, 'pdfs/test.pdf')
    assert nb.get_destination('copy_tests/test.pdf', 'pdfs/') == os.path.join(loc, nb.STATIC_DIR, 'pdfs/test.pdf')
    assert nb.get_destination('copy_tests/subdir', '') == os.path.join(loc, nb.STATIC_DIR, 'subdir/')
    assert nb.get_destination('copy_tests/subdir', 'subdir') == os.path.join(loc, nb.STATIC_DIR, 'subdir/subdir/')
    print nb.get_destination('copy_tests/subdir', 'testout'), os.path.join(loc, nb.STATIC_DIR, 'testout/')
    assert nb.get_destination('copy_tests/subdir', 'testout') == os.path.join(loc, nb.STATIC_DIR, 'testout/')

@patch('scribbler.notebook.Notebook.settings', mock_settings)
def copy_test():
    """
    Tests Notebook.copy_in() method.
    """
    fname = 'copy_tests/test.pdf'
    nb.copy_in(fname, overwrite=True)
    assert not os.path.samefile(fname, nb.get_destination(fname))
    assert cmp(fname, nb.get_destination(fname))

@raises(OSError)
@patch('scribbler.notebook.Notebook.settings', mock_settings)
def copy_error_test():
    """
    Checks Notebook.copy_in() raises appropriate exception if file already exists.
    """
    fname = 'copy_tests/test.pdf'
    nb.copy_in(fname, overwrite=True)
    nb.copy_in(fname, overwrite=False)

@patch('scribbler.notebook.Notebook.settings', mock_settings)
def copy_error_test():
    """
    Checks Notebook.copy_in() will overwrite existing file if told to.
    """
    fname = 'copy_tests/test.pdf'
    nb.copy_in(fname, overwrite=True)
    nb.copy_in(fname, overwrite=True)

@patch('scribbler.notebook.Notebook.settings', mock_settings)
def link_test():
    """
    Tests Notebook.link_in() method.
    """
    fname = 'copy_tests/test.ps'
    nb.link_in(fname, overwrite=True)
    assert os.path.samefile(fname, nb.get_destination(fname))

@raises(OSError)
@patch('scribbler.notebook.Notebook.settings', mock_settings)
def link_error_test():
    """
    Checks Notebook.link_in() raises appropriate exception if file already exists.
    """
    fname = 'copy_tests/test.ps'
    nb.link_in(fname, overwrite=True)
    nb.link_in(fname, overwrite=False)

@patch('scribbler.notebook.Notebook.settings', mock_settings)
def link_error_test():
    """
    Checks Notebook.link_in() will overwrite existing file if told to.
    """
    fname = 'copy_tests/test.ps'
    nb.link_in(fname, overwrite=True)
    nb.link_in(fname, overwrite=True)

@patch('scribbler.notebook.Notebook.settings', mock_settings)
def symlink_test():
    """
    Tests Notebook.symlink_in() method.
    """
    fname = 'copy_tests/test.ps'
    nb.symlink_in(fname, overwrite=True)
    assert os.path.samefile(fname, nb.get_destination(fname))

@raises(OSError)
@patch('scribbler.notebook.Notebook.settings', mock_settings)
def symlink_error_test():
    """
    Checks Notebook.symlink_in() raises appropriate exception if file already exists.
    """
    fname = 'copy_tests/think.txt'
    nb.symlink_in(fname, overwrite=True)
    nb.symlink_in(fname, overwrite=False)

@patch('scribbler.notebook.Notebook.settings', mock_settings)
def symlink_error_test():
    """
    Checks Notebook.symlink_in() will overwrite existing file if told to.
    """
    fname = 'copy_tests/thing.txt'
    nb.symlink_in(fname, overwrite=True)
    nb.symlink_in(fname, overwrite=True)

def settings_test():
    """
    Checks that the Notebook object returns the proper settings dictionary.
    """
    control = {'author': 'Chris MacMackin',
               'email': 'cmacmackin@gmail.com',
               'country': 'Canada',
               'plugins': ['thing'],
               'filetypes': {'ps': 'postscript', 'ps.gz': 'postscript'},
              }
    expected = copy(nb.DEFAULT_SETTINGS)
    for key in ['author', 'email', 'country']:
        expected[key] = control[key]
    expected['plugins'] = copy(nb.PELICAN_PLUGINS)
    expected['plugins'].extend(control['plugins'])
    expected['filetypes'] = copy(nb.FILETYPES)
    expected['filetypes']['ps'] = control['filetypes']['ps']
    expected['filetypes']['ps.gz'] = control['filetypes']['ps.gz']
    ymlfile = open(os.path.join(loc, 'notebook.yml'), 'w')
    yaml.dump(control, ymlfile)
    yaml.dump(control)
    ymlfile.close()
    nb.settings_mod_time = 0
    settings = nb.settings
    assert settings == expected
    settings2 = nb.settings
    assert settings is settings2
    sleep(0.005)
    ymlfile = open(os.path.join(loc, 'notebook.yml'), 'a')
    ymlfile.write('address: True\n')
    ymlfile.close()
    settings3 = nb.settings
    expected['address'] = True
    assert settings3 == expected
    os.remove(os.path.join(loc, 'notebook.yml'))

def teardown_settings():
    os.remove(os.path.join(loc, 'notebook.yml'))

@with_setup(setup_null, teardown_settings)
@raises(TypeError)
def settings_error_test():
    """
    Checks that Notebook.settings will object if wrong data type is given.
    """
    control = {'author': 'Chris MacMackin',
               'email': 'cmacmackin@gmail.com',
               'country': True,
               'plugins': ['thing'],
               'filetypes': {'ps': 'postscript', 'ps.gz': 'postscript'},
              }
    ymlfile = open(os.path.join(loc, 'notebook.yml'), 'w')
    yaml.dump(control, ymlfile)
    yaml.dump(control)
    ymlfile.close()
    nb.settings_mod_time = 0
    settings = nb.settings
    
def mkdirs_test():
    """
    Tests Notebook.mkdirs() create new directories as needed and doesn't raise exception if exists.
    """
    subpath = 'one/two/three/four.pdf'
    nb.mkdirs(os.path.join(loc, subpath))
    assert os.path.isdir(os.path.join(loc, os.path.dirname(subpath)))
    nb.mkdirs(os.path.join(loc, subpath))
    os.removedirs(os.path.join(loc, os.path.dirname(subpath)))

def teardown_pelican_settings():
    os.remove(os.path.join(loc, 'notebook.yml'))

@with_setup(setup_null, teardown_pelican_settings)
def pelican_settings_test():
    """
    Checks that Notebook.pelican_settings() returns the correct information.
    """
    control = {'author': 'Chris MacMackin',
               'email': 'cmacmackin@gmail.com',
               'country': 'Canada',
               'plugins': ['thing'],
               'filetypes': {'ps': 'postscript', 'ps.gz': 'postscript'},
              }
    ymlfile = open(os.path.join(loc, 'notebook.yml'), 'w')
    yaml.dump(control, ymlfile)
    yaml.dump(control)
    ymlfile.close()
    nb.settings_mod_time = 0
    settings = nb.settings
    psettings = nb.pelican_settings
    expected = copy(nb.DEFAULT_PELICAN_SETTINGS)
    expected['OUTPUT_PATH'] = os.path.join(loc, expected['OUTPUT_PATH'])
    expected['PATH'] = os.path.join(loc, expected['PATH'])
    for key in settings:
        if key not in nb.NO_MAPPING:
            expected[nb.PELICAN_MAPPING[key]] = settings[key]
    assert psettings == expected
    psettings2 = nb.pelican_settings
    assert psettings is psettings2
    sleep(0.005)
    ymlfile = open(os.path.join(loc, 'notebook.yml'), 'a')
    ymlfile.write('address: True\n')
    ymlfile.close()
    psettings3 = nb.pelican_settings
    expected[nb.PELICAN_MAPPING['address']] = True
    assert psettings3 == expected

def teardown_pelicanconf():
    os.remove('pelicanconf.py')
    os.remove('pelicanconf.pyc')

@with_setup(setup_null, teardown_pelicanconf)        
@patch('scribbler.notebook.Notebook.pelican_settings', mock_psettings)
def pelicanconf_test():
    """
    Chekcs Notebook.make_pelicaconf() and Notebook.del_pelicanconf() create and delete pelicanconf.py correctly.
    """
    nb.make_pelicanconf()
    shutil.copy(os.path.join(loc, nb.PELICANCONF_FILE), 'pelicanconf.py')
    conf = __import__('pelicanconf')
    conf_dict = vars(conf)
    for key in ['__builtins__', '__doc__', '__file__', '__name__',
                '__package__']:
        del conf_dict[key]
    assert conf_dict == nb.pelican_settings
    assert nb.del_pelicanconf()
    assert not os.path.isfile(os.path.join(loc, nb.PELICANCONF_FILE))
    assert not nb.del_pelicanconf()
        
@raises(NotImplementedError)
def list_test():
    """
    Tests Notebook.list_contents(), which is not yet implemented.
    """
    nb.list_contents()

@raises(ScribblerError)
def newnote_bad_date_test():
    """
    Tests that Notebook.newnote() fails if not given a date of format YYYY-MM-DD HH:mm
    """
    nb.newnote('not a date string', 'Bad Date Test')

@raises(KeyError)
def newnote_bad_markdup_test():
    """
    Tests that Notebook.newnote() fails with unrecognized markup.
    """
    nb.newnote('2015-10-19 20:17', 'Title of Note', markup='svg')

@raises(KeyError)
def newnote_bad_markdup_test():
    """
    Tests that Notebook.newpage() fails with unrecognized markup.
    """
    nb.newpage('Title of Page', markup='svg')

def teardown_newnote():
    for note in nb.notes.values():
        os.remove(os.path.join(loc, note.src_path))
    nb.notes = {}

@with_setup(setup_null, teardown_newnote)
@patch('scribbler.notebook.Notebook.save', mock_save)
@patch('scribbler.content.ScribblerContent.__init__', mock_scribbler_content)
def newnote_test():
    """
    Tests Notebook.newnote() to see that it creates the desired note object and file.
    """
    nb.newnote('2015-10-19 20:17', 'Test Note 1')
    basename = '2015-10-19-test-note-1.md'
    assert cmp(os.path.join(loc, nb.notes[basename].src_path), 'expected/note1.md')
    try:
        nb.newnote('2015-10-19 20:17', 'Test Note 1', 'rst')
        assert False
    except:
        pass
    nb.newnote('2015-10-19 20:17', 'Test Note 2', 'rst')
    basename = '2015-10-19-test-note-2.rst'
    assert cmp(os.path.join(loc, nb.notes[basename].src_path), 'expected/note2.rst')
    nb.newnote('2015-10-19 20:17', 'Test Note 3', 'html')
    basename = '2015-10-19-test-note-3.html'
    assert cmp(os.path.join(loc, nb.notes[basename].src_path), 'expected/note3.html')

def teardown_newpage():
    for ap in nb.appendices.values():
        os.remove(os.path.join(loc, ap.src_path))
    nb.appendices = {}

@with_setup(setup_null, teardown_newpage)
@patch('scribbler.notebook.Notebook.save', mock_save)
@patch('scribbler.content.ScribblerContent.__init__', mock_scribbler_content)
def newpage_test():
    """
    Tests Notebook.newpage() to see that it creates the desired page object and file.
    """
    nb.newpage('Test Page 1')
    basename = 'test-page-1.md'
    assert cmp(os.path.join(loc, nb.appendices[basename].src_path), 
               'expected/page1.md')
    try:
        nb.newnote('Test Page 1', 'rst')
        assert False
    except:
        pass
    nb.newpage('Test Page 2', 'rst')
    basename = 'test-page-2.rst'
    assert cmp(os.path.join(loc, nb.appendices[basename].src_path), 
               'expected/page2.rst')
    nb.newpage('Test Page 3', 'html')
    basename = 'test-page-3.html'
    assert cmp(os.path.join(loc, nb.appendices[basename].src_path), 
               'expected/page3.html')

@patch('scribbler.notebook.Notebook.save', mock_save)
def update_test():
    """
    Tests Notebook.update() is able to add page information in the way that it should.
    """
    testnb = Notebook('test notebook', 'test_notebook')
    testnb.notes['to-be-deleted.md'] = None
    assert 'page1.md' not in testnb.appendices
    assert '2015-10-19-monday.md' not in testnb.notes
    with patch('scribbler.content.ScribblerContent', spec=True) as mock:
        mock.update = mock_update
        testnb.update()
    assert 'to-be-deleted.md' not in testnb.notes
    assert 'page1.md' in testnb.appendices
    assert '2015-10-19-monday.md' in testnb.notes

def setup_save():
    nb.notes['test1'] = 'test value'
    
def teardown_save():
    del nb.notes['test1']
    os.remove('savetest.pkl')

@with_setup(setup_save, teardown_save)
def save_test():
    """
    Tests Notebook.save() properly saves pickled version of itself.
    """
    nb.save('savetest.pkl')
    infile = open('savetest.pkl','r')
    reloaded = load(infile)
    assert reloaded == nb
    
def setup_create():
    os.mkdir('test_with_dir')

def teardown_create():
    shutil.rmtree('test_without_dir')
    
@with_setup(setup_create, teardown_create)
@patch('scribbler.notebook.Notebook.save', mock_save)
@patch('scribbler.notebook.Notebook.update', mock_update)
def create_new_test():
    """
    Tests create_notebook() using an empty and a nonexistant directory.
    """
    testnb = create_notebook('test with dir', 'test_with_dir')
    settings_file = open(os.path.join('test_with_dir', nb.SETTINGS_FILE),'r')
    yaml_settings = yaml.load(settings_file)
    settings_file.close()
    assert yaml_settings['notebook name'] == 'test with dir'
    assert len(yaml_settings.keys()) == 1
    assert testnb.location == os.path.abspath('test_with_dir')
    assert os.path.isdir(os.path.join('test_with_dir', testnb.NOTE_DIR))
    assert os.path.isdir(os.path.join('test_with_dir', testnb.HTML_DIR))
    assert os.path.isdir(os.path.join('test_with_dir', testnb.PDF_DIR))
    assert os.path.isdir(os.path.join('test_with_dir', testnb.APPE_DIR))
    assert os.path.isdir(os.path.join('test_with_dir', testnb.STATIC_DIR))
    shutil.copy('test_notebook/notebook.yml', 'test_with_dir/notebook.yml')
    testnb = create_notebook('test with dir', 'test_with_dir')
    assert cmp('test_notebook/notebook.yml', 'test_with_dir/notebook.yml')
    shutil.rmtree('test_with_dir')
    testnb = create_notebook('test with dir', 'test_without_dir')
    settings_file = open(os.path.join('test_without_dir', nb.SETTINGS_FILE),'r')
    yaml_settings = yaml.load(settings_file)
    settings_file.close()
    assert yaml_settings['notebook name'] == 'test with dir'
    assert len(yaml_settings.keys()) == 1
    assert testnb.location == os.path.abspath('test_without_dir')
    assert os.path.isdir(os.path.join('test_without_dir', testnb.NOTE_DIR))
    assert os.path.isdir(os.path.join('test_without_dir', testnb.HTML_DIR))
    assert os.path.isdir(os.path.join('test_without_dir', testnb.PDF_DIR))
    assert os.path.isdir(os.path.join('test_without_dir', testnb.APPE_DIR))
    assert os.path.isdir(os.path.join('test_without_dir', testnb.STATIC_DIR))

@patch('scribbler.notebook.Notebook.save', mock_save)
@patch('scribbler.notebook.Notebook.update', mock_update)
def create_existing_test():
    """
    Tests create_notebook() using a notebook in an existing directory.
    """
    testnb = create_notebook('test notebook', 'test_notebook')
    infile = open(os.path.join('test_notebook', nb.STORAGE_FILE), 'r')
    reloaded = load(infile)
    print testnb.__dict__
    print reloaded.__dict__
    assert testnb == reloaded

def setup_build():
    shutil.move(os.path.join('test_notebook', nb.STORAGE_FILE), 'backup.pkl')

def teardown_build():
    shutil.move('backup.pkl', os.path.join('test_notebook', nb.STORAGE_FILE))
    shutil.rmtree('test_notebook/pdf')
    os.mkdir('test_notebook/pdf')
    shutil.rmtree('test_notebook/html')
    os.mkdir('test_notebook/html')
    
@with_setup(setup_build, teardown_build)
@patch('scribbler.notebook.Notebook.save', mock_save)
def build_test():
    """
    Tests Notebook.build() actually produces a notebook with appropriate HTML and PDF.
    Note that this is not really a proper unit test, as using other methods is pretty
    much unavoidable in this case.
    """
    # TODO: Make this into a proper unit test, independent of other methods
    testnb = create_notebook('test notebook', 'test_notebook')
    testnb.build()
    assert os.path.isfile('test_notebook/html/notes/2015-10-19-monday.html')
    assert os.path.isfile('test_notebook/html/notes/2015-10-20-tuesday.html')
    assert os.path.isfile('test_notebook/html/pages/page1.html')
    assert os.path.isfile('test_notebook/html/pages/page2.html')
    assert os.path.isfile('test_notebook/html/index.html')
    assert os.path.isfile('test_notebook/pdf/2015-10-19-monday.pdf')
    assert os.path.isfile('test_notebook/pdf/2015-10-20-tuesday.pdf')
    assert os.path.isfile('test_notebook/pdf/page1.pdf')
    assert os.path.isfile('test_notebook/pdf/page2.pdf')
    assert not os.path.isdir(os.path.join(testnb.location, testnb.CONTENT_DIR))
    page1t = os.path.getmtime('test_notebook/pdf/page1.pdf')
    page2t = os.path.getmtime('test_notebook/pdf/page2.pdf')
    os.utime('test_notebook/appendices/page2.md', None)
    testnb.build()
    assert page1t == os.path.getmtime('test_notebook/pdf/page1.pdf')
    assert page2t < os.path.getmtime('test_notebook/pdf/page2.pdf')

def equals_test():
    """
    Checks the overloaded equivalency operator for the Notebook class.
    """
    assert nb == nb
    testnb = copy(nb)
    testnb.location = 'none'
    assert nb != testnb
    assert nb != 'string'

@patch('scribbler.content.ScribblerContent.__init__')
@patch('scribbler.notebook.Notebook.save', mock_save)
def add_note_test(add):
    """
    Checks that Notebook.add_note() behaves correctly. 
    """
    testnb = Notebook('test notebook', 'test_notebook')
    add.return_value = None
    testnb.addnote('2015-10-27', 'Test', 'test.md')
    add.assert_called_with('Test', '2015-10-27', '../../test.md', testnb)
    testnb.addnote('2015-10-27', 'Test', 'test_notebook/notes/test.md')
    add.assert_called_with('Test', '2015-10-27', 'test.md', testnb)
    testnb.addnote('2015-10-27', 'Test 2', 'test_notebook/notes/test.md', True)
    add.assert_called_with('Test 2', '2015-10-27', 'test.md', testnb)

@raises(ScribblerError)
def add_note_bad_date_test():
    """
    Checks error raised when malformed date passed to Notebook.add_note(). 
    """
    nb.addnote('2015-20-27', 'Test', 'test.md')

@raises(ScribblerError)
def add_note_existing_test():
    """
    Checks error raised when Notebook.add_note() tries to add a note in existing file. 
    """
    testnb = Notebook('test notebook', 'test_notebook')
    testnb.notes['test.md'] = None
    testnb.addnote('2015-10-27', 'Test', 'test_notebook/notes/test.md')
    
@patch('scribbler.content.ScribblerContent.__init__')
@patch('scribbler.notebook.Notebook.save', mock_save)
def add_page_test(add):
    """
    Tests Notebook.add_page() behave correctly.
    """
    testnb = Notebook('test notebook', 'test_notebook')
    add.return_value = None
    testnb.addpage('Test', 'test.md')
    add.assert_called_with('Test', '????-??-??', '../../test.md', testnb)
    testnb.addpage('Test', 'test_notebook/appendices/test.md')
    add.assert_called_with('Test', '????-??-??', 'test.md', testnb)
    testnb.addpage('Test 2', 'test_notebook/appendices/test.md', True)
    add.assert_called_with('Test 2', '????-??-??', 'test.md', testnb)

@raises(ScribblerError)
def add_page_existing_test():
    """
    Checks error raised when Notebook.add_note() tries to add a note in existing file. 
    """
    testnb = Notebook('test notebook', 'test_notebook')
    testnb.appendices['test.md'] = None
    testnb.addpage('Test', 'test_notebook/appendices/test.md')
    
