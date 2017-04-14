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
Unit tests for the CLI of Scribbler.
"""

import os.path
import shutil
from tempfile import mkdtemp
from filecmp import cmp
from copy import copy
from time import sleep
from pickle import load
from datetime import datetime, timedelta

import scribbler as scr

from mock import MagicMock, patch
from nose.tools import *
import yaml
from click import command, argument, option
from click.testing import CliRunner

# Common variables to use for a test notebook
location = None

def setup_module():
    """
    Create a notebook and directory tree on which to perform tests.
    """
    global location
    infile = open(os.path.join('database','test-notebook.pkl'),'r')
    loaded = load(infile)
    scr.cur_notebook = loaded
    location = scr.cur_notebook.location

def teardown_module():
    """
    Remove directory tree in which tests were performed.
    """


def setup_null():
    pass


def mock_iter(self):
    """
    Replaces Notebook.__iter__() with a stub returning an empty iterable.
    """
    nb = MagicMock()
    nb.name = 'test'
    nb.location = '.'
    return iter([nb])


def check_loaded_test():
    """
    Check that the check_if_loaded() subroutine works when passed a Notebook object.
    """
    infile = open(os.path.join('database','test-notebook.pkl'),'r')
    manual_loaded = load(infile)
    scr.check_if_loaded(manual_loaded)

def check_loaded_fails_test():
    """
    Ensure check_if_loaded exits if passed something other than a Notebook object.
    """
    for obj in [None, 'notebook', 1]:
        yield check_loaded_fails, obj

@raises(SystemExit)
def check_loaded_fails(obj):
    scr.check_if_loaded(obj)

@patch('click.launch')
@patch('scribbler.check_if_loaded', lambda x: None)
def cd_test(launch):
    """
    Tests the `scribbler cd` command works.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['cd'])
    assert result.exit_code == 0
    launch.assert_called_with(location)
    
def today_test():
    """
    Tests the `scribbler today` command works (i.e. says is not yet implemented)
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['today'])
    assert 'Not yet implemented.' in result.output

@patch('scribbler.notebook.Notebook.newpage')
@patch('scribbler.check_if_loaded', lambda x: None)
def newappendix_test(newpage):
    """
    Tests creation of a new page using `scribbler newappendix`.
    """
    runner = CliRunner()
    t = '"a b c d e"'
    m = 'rst'
    result = runner.invoke(scr.cli, ['newappendix', '-m', m, t])
    newpage.assert_called_with(t, m)

@patch('scribbler.notebook.Notebook.addpage')
@patch('scribbler.check_if_loaded', lambda x: None)
def addappendix_test(addpage):
    """
    Tests creation of adding a page record using `scribbler addappendix`.
    """
    runner = CliRunner()
    t = '"a b c d e"'
    p = 'test_notebook/notes/2015-10-19-monday.md'
    result = runner.invoke(scr.cli, ['addappendix', p, t])
    addpage.assert_called_with(t, p, False)

@patch('scribbler.notebook.Notebook.newnote')
@patch('scribbler.check_if_loaded', lambda x: None)
def newnote_test(newnote):
    """
    Tests creation of a new note using `scribbler newnote`.
    """    
    runner = CliRunner()
    t = '"a b c d e"'
    m = 'rst'
    d = datetime.now()
    result = runner.invoke(scr.cli, ['newnote', '-m', m, '-t', t])
    try:
        newnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), t, m) 
    except AssertionError:
        d -= timedelta(minutes=1)
        newnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), t, m)
    result = runner.invoke(scr.cli, ['newnote', '-m', m])
    try:
        newnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), d.strftime('%A'), m) 
    except AssertionError:
        d -= timedelta(minutes=1)
        newnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), d.strftime('%A'), m)

@patch('scribbler.notebook.Notebook.addnote')
@patch('scribbler.check_if_loaded', lambda x: None)
def addnote_test(addnote):
    """
    Tests registering existin file as note using `scribbler addnote`.
    """    
    runner = CliRunner()
    t = '"a b c d e"'
    d = datetime.now()
    p = 'test_notebook/notes/2015-10-19-monday.md'
    result = runner.invoke(scr.cli, ['addnote', '-t', t, p])
    try:
        addnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), t, p, False) 
    except AssertionError:
        d -= timedelta(minutes=1)
        addnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), t, p, False)
    result = runner.invoke(scr.cli, ['addnote', '--overwrite', p])
    try:
        addnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), d.strftime('%A'), p, True) 
    except AssertionError:
        d -= timedelta(minutes=1)
        addnote.assert_called_with(d.strftime('%Y-%m-%d %H:%M'), d.strftime('%A'), p, True)


@patch('scribbler.notebook.Notebook.build')
@patch('scribbler.check_if_loaded', lambda x: None)
def build_test(build):
    """
    Tests building of notebook using `scribbler build`.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['build'])
    build.assert_called_with()

@patch('scribbler.database.ScribblerDatabase.unload')
def unload_test(unload):
    """
    Tests `scribbler unload` calls appropriate method.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['unload'])
    unload.assert_called_with()

@patch('scribbler.database.ScribblerDatabase.load')
def load_test(load):
    """
    Tests `scribbler load` calls appropriate method.
    """
    runner = CliRunner()
    nb = 'thingy'
    result = runner.invoke(scr.cli, ['load', nb])
    load.assert_called_with(nb)

@patch('scribbler.database.ScribblerDatabase.__iter__', mock_iter)
def list_test():
    """
    Tests correct output is generated by `scribbler list`.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['list'])
    assert 'The following notebooks are known to Scribbler:' in result.output
    assert '\ttest                    \t.' in result.output
    
@patch('scribbler.database.ScribblerDatabase.delete')
def forget_test(delete):
    """
    Tests `scribbler forget` calls appropriate method.
    """
    runner = CliRunner()
    t = 'notebook name'
    result = runner.invoke(scr.cli, ['forget', t, '--delete'], input='y\n')
    delete.assert_called_with(t, True)
    result = runner.invoke(scr.cli, ['forget', t], input='y\n')
    delete.assert_called_with(t, False)

@patch('scribbler.database.ScribblerDatabase.add')
def init_test(add):
    """
    Checks `scribbler init` calls appropriate method.
    """
    runner = CliRunner()
    t = 'notebook name'
    result = runner.invoke(scr.cli, ['init', t, 'test_notebook'])
    add.assert_called_with(t, 'test_notebook')

@patch('scribbler.notebook.Notebook.mkdirs')
@patch('scribbler.add_file')
@patch('scribbler.check_if_loaded', lambda x: None)
def copy_test(add_file, mkdirs):
    """
    Checks `scribbler copy` calls appropriate methods and encounters expected errors.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['copy', 'copy_tests/subdir/'])
    assert "Error: Path 'copy_tests/subdir/' is a directory. Run with option -R." in result.output
    result = runner.invoke(scr.cli, ['copy', 'copy_tests/subdir/subfile1.md'])
    add_file.assert_called_with(scr.cur_notebook.copy_in, 
                                'copy_tests/subdir/subfile1.md', None, force=False)
    result = runner.invoke(scr.cli, ['copy', 'copy_tests/subdir/subfile1.md', '-d',
                                     'test.md', '-f'])
    add_file.assert_called_with(scr.cur_notebook.copy_in, 
                                'copy_tests/subdir/subfile1.md', 'test.md',
                                force=True)
    result = runner.invoke(scr.cli, ['copy', 'copy_tests/subdir/', '-R'])
    add_file.assert_any_call(scr.cur_notebook.copy_in,
                             'copy_tests/subdir/subsubdir/thing.html', None,
                             force=False)
    add_file.assert_any_call(scr.cur_notebook.copy_in,
                             'copy_tests/subdir/subfile1.md', None,
                             force=False)
    result = runner.invoke(scr.cli, ['copy', 'copy_tests/subdir/', '-R',
                                     '-d', 'output'])
    add_file.assert_any_call(scr.cur_notebook.copy_in,
                             'copy_tests/subdir/subsubdir/thing.html', 
                             'output/subsubdir/thing.html',
                             force=False)
    add_file.assert_any_call(scr.cur_notebook.copy_in,
                             'copy_tests/subdir/subfile1.md', 
                             'output/subfile1.md',
                             force=False)
    
@patch('scribbler.notebook.Notebook.mkdirs')
@patch('scribbler.add_file')
@patch('scribbler.check_if_loaded', lambda x: None)
def link_test(add_file, mkdirs):
    """
    Checks `scribbler link` calls appropriate methods and encounters expected errors.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['link', 'copy_tests/subdir/'])
    assert "Error: Path 'copy_tests/subdir/' is a directory. Run with option -R." in result.output
    result = runner.invoke(scr.cli, ['link', 'copy_tests/subdir/subfile1.md'])
    add_file.assert_called_with(scr.cur_notebook.link_in, 
                                'copy_tests/subdir/subfile1.md', None, force=False)
    result = runner.invoke(scr.cli, ['link', 'copy_tests/subdir/subfile1.md', '-d',
                                     'test.md', '-f'])
    add_file.assert_called_with(scr.cur_notebook.link_in, 
                                'copy_tests/subdir/subfile1.md', 'test.md',
                                force=True)
    result = runner.invoke(scr.cli, ['link', 'copy_tests/subdir/', '-R'])
    add_file.assert_any_call(scr.cur_notebook.link_in,
                             'copy_tests/subdir/subsubdir/thing.html', None,
                             force=False)
    add_file.assert_any_call(scr.cur_notebook.link_in,
                             'copy_tests/subdir/subfile1.md', None,
                             force=False)
    result = runner.invoke(scr.cli, ['link', 'copy_tests/subdir/', '-R',
                                     '-d', 'output'])
    add_file.assert_any_call(scr.cur_notebook.link_in,
                             'copy_tests/subdir/subsubdir/thing.html', 
                             'output/subsubdir/thing.html',
                             force=False)
    add_file.assert_any_call(scr.cur_notebook.link_in,
                             'copy_tests/subdir/subfile1.md', 
                             'output/subfile1.md',
                             force=False)
    
@patch('scribbler.notebook.Notebook.mkdirs')
@patch('scribbler.add_file')
@patch('scribbler.check_if_loaded', lambda x: None)
def symlink_test(add_file, mkdirs):
    """
    Checks `scribbler symlink` calls appropriate methods.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['symlink', 'copy_tests/subdir/'])
    add_file.assert_called_with(scr.cur_notebook.symlink_in, 
                                'copy_tests/subdir/', None, force=False)
    result = runner.invoke(scr.cli, ['symlink', 'copy_tests/subdir/subfile1.md'])
    add_file.assert_called_with(scr.cur_notebook.symlink_in, 
                                'copy_tests/subdir/subfile1.md', None, force=False)
    result = runner.invoke(scr.cli, ['symlink', 'copy_tests/subdir/subfile1.md', '-d',
                                     'test.md', '-f'])
    add_file.assert_called_with(scr.cur_notebook.symlink_in, 
                                'copy_tests/subdir/subfile1.md', 'test.md',
                                force=True)
    result = runner.invoke(scr.cli, ['symlink', 'copy_tests/subdir/', '-R'])
    add_file.assert_any_call(scr.cur_notebook.symlink_in,
                             'copy_tests/subdir/subsubdir/thing.html', None,
                             force=False)
    add_file.assert_any_call(scr.cur_notebook.symlink_in,
                             'copy_tests/subdir/subfile1.md', None,
                             force=False)
    result = runner.invoke(scr.cli, ['symlink', 'copy_tests/subdir/', '-R',
                                     '-d', 'output'])
    add_file.assert_any_call(scr.cur_notebook.symlink_in,
                             'copy_tests/subdir/subsubdir/thing.html', 
                             'output/subsubdir/thing.html',
                             force=False)
    add_file.assert_any_call(scr.cur_notebook.symlink_in,
                             'copy_tests/subdir/subfile1.md', 
                             'output/subfile1.md',
                             force=False)

@patch('scribbler.notebook.Notebook.get_destination')
@patch('os.path.isfile')
@patch('scribbler.check_if_loaded', lambda x: None)
def add_file_test(isfile, getdest):
    """
    Checks that the add_file() method behaves correctly under various circumstances.
    """
    @command()
    @argument('src')
    @argument('dest')
    @option('--force', '-f', is_flag=True)
    def click_mock(src, dest, force):
        scr.add_file(method, src, dest, scr.cur_notebook, force)

    def side_effect1(*args):
        if not args[3]:
            raise OSError
        else:
            pass
            
    method = MagicMock()
    scr.add_file(method, 'src', 'dest', scr.cur_notebook, True)
    method.assert_called_with(scr.cur_notebook, 'src', 'dest', True)
    method = MagicMock(side_effect=side_effect1)
    runner = CliRunner()
    result = runner.invoke(click_mock, ['src', 'dest'], input='y\n')
    method.assert_any_call(scr.cur_notebook, 'src', 'dest', False)
    method.assert_called_with(scr.cur_notebook, 'src', 'dest', True)
    
    method = MagicMock(side_effect=(OSError('1'), None))
    isfile.side_effect=[True, False]
    getdest.return_value = 'dest'
    result = runner.invoke(click_mock, ['src', 'dest'], input='\n-\n')
    assert 'Placing this file in the notebook would' in result.output
    assert 'Provide a new filename' in result.output
    method.assert_called_with(scr.cur_notebook, 'src', 'dest', False)
    assert method.call_count == 1
    
    method = MagicMock(side_effect=(OSError('1'), None))
    getdest.return_value = 'dest.txt'
    isfile.side_effect=[True, False]
    result = runner.invoke(click_mock, ['src', 'dest.txt'], input='\n\n')
    method.assert_called_with(scr.cur_notebook, 'src', 'dest-1.txt', False)

    method = MagicMock(side_effect=(OSError('1'), None))
    getdest.return_value = 'dest.txt'
    isfile.side_effect=[True, False, False]
    result = runner.invoke(click_mock, ['src', 'dest.txt'], input='\nthingy.txt\n')
    method.assert_called_with(scr.cur_notebook, 'src', 'thingy.txt', False)

    method = MagicMock(side_effect=(OSError('1'), None))
    getdest.return_value = 'out/dest.txt'
    isfile.side_effect=[True, False]
    result = runner.invoke(click_mock, ['src', 'out/dest.txt'], input='\n\n')
    method.assert_called_with(scr.cur_notebook, 'src', 'out/dest-1.txt', False)

def status_test():
    """
    Checks that `scribbler status` outputs a list of notes and appendices.
    """
    runner = CliRunner()
    result = runner.invoke(scr.cli, ['status'])
    expected = 'Notebook: test notebook\nLocation: /home/chris/Code/scribbler/'\
               'tests/test_notebook\n\nContains 2 notes:'
    assert expected in result.output
