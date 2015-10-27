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
Unit tests for the ScribblerDatabase class
"""

import os.path
import shutil
from collections import namedtuple
from pickle import load
import warnings

from scribbler.database import ScribblerDatabase
from scribbler.notebook import Notebook
from scribbler.content  import ScribblerContent
from scribbler.errors import ScribblerError, ScribblerWarning

from mock import MagicMock, patch
from nose.tools import *
from pelican.utils import slugify

db = None
testloc = 'test_database_directory_creation'

def setup_module():
    """
    Create a notebook and directory tree on which to perform tests.
    """
    global db
    db = ScribblerDatabase('database')
    assert db.scribbler_dir == 'database'
    try: shutil.rmtree(testloc)
    except: pass

def teardown_module():
    """
    Remove directory tree in which tests were performed.
    """
    try: shutil.rmtree(testloc)
    except: pass


def mock_get(self, name):
    infile = open(os.path.join(db.scribbler_dir,'test-notebook.pkl'),'r')
    loaded = load(infile)
    loaded.location = testloc
    return loaded
    
def mock_save(self, path):
    """
    Replaces Notebook.save() with a stub creating an empty file.
    """
    with open(path, 'w') as f:
        pass

def mock_to_filename(self, name):
    return 'magic-notebook.pkl'

def mock_iter(self):
    """
    Replaces Notebook.__iter__() with a stub returning an empty iterable.
    """
    return iter([])


def setup_null():
    pass


def teardown_mkdir():
    os.rmdir(testloc)

@with_setup(setup_null, teardown_mkdir)
def init_mkdir_test():
    """
    Tests ScribblerDatabase constructor when directory does not exist. 
    """
    try: shutil.rmtree(testloc)
    except: pass
    testdb = ScribblerDatabase(testloc)
    assert testdb.scribbler_dir == testloc
    assert os.path.isdir(testloc)

def to_filename_test():
    """
    Test generator to check ScribblerDatabase.name_to_filename() returns appropriate filenames.
    """
    for name in ['Thing thing thing', 'tell/me/this/is/alright', 'No BLOODY iDeA!!']:
        yield check_filenames, name, db.name_to_filename(name)
        
def check_filenames(nb_name, filename):
    """
    Tests FILENAME is correct name of file containing notebook with name NB_NAME.
    """
    assert filename == slugify(nb_name) + '.pkl'
    
def get_test():
    """
    Tests ScribblerDatabase.get() returns an appropriate Notebook object.
    """
    infile = open(os.path.join(db.scribbler_dir,'test-notebook.pkl'),'r')
    manual_loaded = load(infile)
    assert manual_loaded == db.get('test notebook')
    assert manual_loaded == db.get('Test Notebook')
    
@raises(ScribblerError)
def get_nonexistent_test():
    """
    Tests ScribblerDatabase.get() raises an error if no records of a notebook exist.
    """
    db.get('does not exist')

def teardown_save():
    try: os.remove(os.path.join(db.scribbler_dir, 'newnotebook.pkl'))
    except: pass

@with_setup(setup_null, teardown_save)
@patch('scribbler.database.ScribblerDatabase.__iter__', mock_iter)
@patch('scribbler.notebook.Notebook.__init__', MagicMock(return_value=None))
@patch('scribbler.notebook.Notebook.save')
def add_test(save):
    """
    Checks that ScribblerDatabase.add() tries to create and save a notebook.
    """
    db.add('newnotebook', 'newnotebookdir')
    Notebook.__init__.assert_called_with('newnotebook', 'newnotebookdir')
    save.assert_called_with(os.path.join(db.scribbler_dir, 'newnotebook.pkl'))

@raises(ScribblerError)
def add_exists_test():
    """
    Checks error raised when ScribblerDatabase.add() asked to make notebook with name already in use.
    """
    db.add('test notebook', 'testdir')
    
@raises(ScribblerError)
def add_similar_test():
    """
    Checks error raised when ScribblerDatabase.add() asked to make notebook with name similar to one already in use.
    """
    db.add('Test Notebook', 'testdir')
    
@raises(ScribblerError)
def add_loc_used_test():
    """
    Checks error raised when ScribblerDatabase.add() asked to make notebook with same location as existing notebook.
    """
    db.add('Test Notebook 2', 'test_notebook')

@raises(ScribblerError)
def add_not_dir_test():
    """
    Checks error raised when ScribblerDatabase.add() asked to make notebook with same location as existing file.
    """
    db.add('Test Notebook 2', 'database_test.py')

def setup_delete():
    os.mkdir(testloc)
    fname = os.path.join(db.scribbler_dir, 'test-delete.pkl')
    with open(fname, 'w') as a:
        pass

def teardown_delete():
    try: shutil.rmtree(testloc)
    except: pass
    try: os.remove(os.path.join(db.scribbler_dir, 'test-delete.pkl'))
    except: pass

@with_setup(setup_delete, teardown_delete)
@patch('scribbler.database.ScribblerDatabase.unload')
@patch('scribbler.database.ScribblerDatabase.is_current')
@patch('scribbler.database.ScribblerDatabase.get', mock_get)
def  delete_test(unload, iscur):
    """
    Ensures ScribblerDatabase.delete() fully deletes a notebook.
    """
    iscur.return_value = True
    fname = os.path.join(db.scribbler_dir, 'test-delete.pkl')
    assert os.path.isfile(fname)
    assert os.path.isdir(testloc)
    db.delete('Test Delete', True)
    unload.assert_called_with('Test Delete')
    assert not os.path.isdir(testloc)
    assert not os.path.isfile(fname)

@raises(ScribblerWarning)
@with_setup(setup_delete, teardown_delete)
@patch('scribbler.database.ScribblerDatabase.unload')
@patch('scribbler.database.ScribblerDatabase.is_current')
@patch('scribbler.database.ScribblerDatabase.get', mock_get)
def delete_warning_test(unload, iscur):
    """
    Checks that a warning is raised if ScribblerDatabase.delete() can not remove notebook's directory.
    """
    warnings.simplefilter('error', ScribblerWarning)
    iscur.return_value = True
    fname = os.path.join(db.scribbler_dir, 'test-delete.pkl')
    assert os.path.isfile(fname)
    shutil.rmtree(testloc)
    db.delete('Test Delete', True)    

def setup_load():
    try: os.remove(os.path.join(db.scribbler_dir, db.LOADED_NAME))
    except: pass

@with_setup(setup_load, setup_load)
@patch('scribbler.database.ScribblerDatabase.unload')
def load_test(unload):
    """
    Checks that ScribblerDatabase.load() creates appropriate symlink.
    """
    db.load('Test Notebook')
    unload.assert_called_with()
    assert os.path.islink(os.path.join(db.scribbler_dir, db.LOADED_NAME))
    assert os.path.isfile(os.path.join(db.scribbler_dir, db.LOADED_NAME))
    assert os.path.samefile(os.path.join(db.scribbler_dir, db.LOADED_NAME), 
                            os.path.join(db.scribbler_dir, 'test-notebook.pkl'))

@raises(ScribblerError)
@with_setup(setup_load, setup_load)
@patch('scribbler.database.ScribblerDatabase.unload')
def load_fails_test(unload):
    """
    Checks error raised if ScribblerDatabase.load() can not find notebook.
    """
    db.load('Does Not Exist')
    unload.assert_called_with()
    assert not os.path.islink(os.path.join(db.scribbler_dir, db.LOADED_NAME))

def setup_unload():
    with open(os.path.join(db.scribbler_dir, db.LOADED_NAME), 'w') as f:
        pass
    
@with_setup(setup_unload, setup_load)
def unload_test():
    """
    Checks ScribblerDatabase.unload() deletes appropriate link file.
    """
    assert os.path.isfile(os.path.join(db.scribbler_dir, db.LOADED_NAME))
    db.unload()
    assert not os.path.isfile(os.path.join(db.scribbler_dir, db.LOADED_NAME))
    db.unload()
    assert not os.path.isfile(os.path.join(db.scribbler_dir, db.LOADED_NAME))
    
def setup_current():
    os.symlink('./test-notebook.pkl',os.path.join(db.scribbler_dir, db.LOADED_NAME))
    
@with_setup(setup_current, setup_load)
def is_current_test():
    """
    Checks ScribblerDatabase.is_current() correctly identifies if named notebook is loaded.
    """
    assert db.is_current('Test Notebook')
    assert not db.is_current('Not A Real Notebook')
    
@with_setup(setup_current, setup_load)
def current_test():
    """
    Checks ScribblerDatabase.current() returns correct notebook object.
    """
    assert db.current() == db.get('Test Notebook')

@patch('scribbler.database.ScribblerDatabase.name_to_filename', mock_to_filename)
def save_test():
    """
    Checks ScribblerDatabase.save() calls the methods it should.
    """
    nb = MagicMock()
    nb.name = 'Magic Notebook'
    db.save(nb)
    nb.save.assert_called_with(os.path.join(db.scribbler_dir, mock_to_filename(1, 1)))

