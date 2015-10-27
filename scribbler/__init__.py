#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
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
Scribbler
=========

Scribbler is a wrapper for the Pelican static-site generator. It configures
Pelican to produce a notebook, with the particular emphasis being on notes
for scientific research. Pelican will output the notebook in HTML format and
Scribbler will produce PDFs from these HTML pages as well.
"""

import datetime
import os
import sys
import warnings

import click

from .database import ScribblerDatabase
from .notebook import Notebook
from .errors import ScribblerWarning

__appname__    = "FORD"
__author__     = "Chris MacMackin"
__maintainer__ = "Chris MacMackin"
__license__    = "GPLv3"
__status__     = "Pre-Alpha"
__version__ = '0.1.0'
#__credits__    = []

dt = datetime.datetime.now()
scribbler = ScribblerDatabase(click.get_app_dir(__appname__))
cur_notebook = scribbler.current()

def check_if_loaded(notebook):
    """
    Raise an error message if no notebook is loaded.
    """
    print notebook
    if not isinstance(notebook,Notebook):
        click.secho('Can not perform this operation: no notebook loaded.',
                    fg='red')
        click.echo('Load a notebook with:\t`scribbler load <notebook name>`')
        sys.exit(1)


@click.group()
@click.version_option(version=__version__)
def cli():
    warnings.simplefilter('always', ScribblerWarning)


@cli.command(help='Copies SRC to the appropriate location within the '
                  'content directory of your notebook. Unless '
                  'otherwise specified, files will be placed in the '
                  'directory corresponding to their file type, as '
                  'specified in the notebook\'s YAML file.')
@click.argument('src', type=click.Path(exists=True))
@click.option('-d','--destination', type=click.Path(),
              help='Destination, relative to the root of the notebook '
                   'content directory, to which SRC is copied.')
@click.option('--recursive', '-R', is_flag=True,
              help='Copy the contents of directories recursively. If a '
                   'destination is specified then the directory tree '
                   'will be reproduced there. Otherwise, the '
                   'individual files will be placed in the default '
                   'location for their filetype.')
@click.option('--force', '-f', is_flag=True,
              help='Overwrite files without asking permission first.')
def copy(src, destination, recursive, force):
    check_if_loaded(cur_notebook)
    if not recursive and os.path.isdir(src):
        click.secho("Error: Path '{}' is a directory. Run with option -R.".format(src),
                    fg='red')
    elif os.path.isdir(src):
        for dirpath, dirnames, filenames in os.walk(src):
            cur_notebook.mkdirs(dirpath)
            for name in filenames:
                if destination:
                    dest = os.path.join(os.path.relpath(dirpath, src), name)
                    dest = os.path.normpath(dest)
                    dest = os.path.join(destination, dest)
                else:
                    dest = None
                add_file(cur_notebook.copy_in, os.path.join(dirpath, name),
                         dest, force=force)
    else:
        add_file(cur_notebook.copy_in, src, destination, force=force)

@cli.command(help='Creates a hard link to SRC, located in DST, where '
                  'DST is evaluated relative to the root of your '
                  'notebook contents.')
@click.argument('src', type=click.Path(exists=True))
@click.option('-d','--destination', type=click.Path(),
              help='Destination, relative to the root of the notebook '
                   'content directory, to which SRC is copied.')
@click.option('--recursive', '-R', '-r', is_flag=True,
              help='Link the contents of directories recursively. If a '
                   'destination is specified then the directory tree '
                   'will be reproduced there. Otherwise, the '
                   'individual links will be placed in the default '
                   'location for their filetype.')
@click.option('--force', '-f', is_flag=True,
              help='Overwrite files without asking permission first.')
def link(src, destination, recursive, force):
    check_if_loaded(cur_notebook)
    if not recursive and os.path.isdir(src):
        click.secho("Error: Path '{}' is a directory. Run with option -R.".format(src),
                    fg='red')
    elif os.path.isdir(src):
        for dirpath, dirnames, filenames in os.walk(src):
            cur_notebook.mkdirs(dirpath)
            for name in filenames:
                if destination:
                    dest = os.path.join(os.path.relpath(dirpath, src), name)
                    dest = os.path.normpath(dest)
                    dest = os.path.join(destination, dest)
                else:
                    dest = None
                add_file(cur_notebook.link_in, os.path.join(dirpath, name),
                         dest, force=force)
    else:
        add_file(cur_notebook.link_in, src, destination, force=force)


@cli.command(help='Creates a SYMLINK to SRC from DST, where DST is '
                  'evaluated relative to the root of your notebook '
                  'contents.')
@click.argument('src', type=click.Path(exists=True))
@click.option('-d','--destination', type=click.Path(),
              help='Destination, relative to the root of the notebook '
                   'content directory, to which SRC is copied.')
@click.option('--recursive', '-R', '-r', is_flag=True,
              help='Link the contents of directories recursively. If a '
                   'destination is specified then the directory tree '
                   'will be reproduced there. Otherwise, the '
                   'individual links will be placed in the default '
                   'location for their filetype. If this option is not '
                   'specified and SRC is a directory, then a link will '
                   'be made to a directory itself.')
@click.option('--force', '-f', is_flag=True,
              help='Overwrite files without asking permission first.')
def symlink(src, destination, recursive, force):
    check_if_loaded(cur_notebook)
    if recursive and os.path.isdir(src):
        for dirpath, dirnames, filenames in os.walk(src):
            cur_notebook.mkdirs(dirpath)
            for name in filenames:
                if destination:
                    dest = os.path.join(os.path.relpath(dirpath, src), name)
                    dest = os.path.normpath(dest)
                    dest = os.path.join(destination, dest)
                else:
                    dest = None
                add_file(cur_notebook.symlink_in, os.path.join(dirpath, name),
                         dest, force=force)
    else:
        add_file(cur_notebook.symlink_in, src, destination, force=force)


@cli.command(help='Create a new notebook with NAME. If a notebook '
                  'already exists in LOCATION then it will be scanned '
                  'for information. Otherwise, Scribbler will create '
                  'the necessary files.')
@click.argument('name', type=click.STRING)
@click.argument('location', type=click.Path(exists=True))
def init(name, location):
    scribbler.add(name, location)


@cli.command(help='Remove notebook NAME from Scribbler\'s records.')
@click.argument('name', type=click.STRING)
@click.confirmation_option(help='Are you sure you want to forget this '
                                'notebook?')
@click.option('--delete/--no-delete', default=False,
              help='Delete the contents of the notebook.')
def forget(name, delete):
    scribbler.delete(name, delete)


@cli.command(help='Load notebook NAME, meaning that Scribbler '
                  'operations will act on it.')
@click.argument('name', type=click.STRING)
def load(name):
    scribbler.load(name)


@cli.command(help='Unload the currently loaded notebook from '
                  'Scribbler. Scribbler commands will no longer work '
                  'on a notebook.')
def unload():
    scribbler.unload()


#~ @cli.command()
#~ def status():
    #~ pass

@cli.command(help='Lists all notebooks known to Scribbler.')
def list():
    click.echo('The following notebooks are known to Scribbler:\n')
    form = '\t{:24}\t{}'
    for nb in scribbler:
        click.echo(form.format(nb.name, nb.location))

    
@cli.command(help='Creates the HTML and PDF output of the currently '
                  'loaded notebook.')
def build():
    check_if_loaded(cur_notebook)
    cur_notebook.build()
    scribbler.save(cur_notebook)


@cli.command(help='Creates a new note in the currently loaded notebook.')
@click.option('--date', '-d', default=dt.strftime('%Y-%m-%d %H:%M'),
              help='Date to use for the new article, in format "YYYY-MM-DD HH:mm".')
@click.option('--title', '-t', default=dt.strftime('%A'),
              help='Title of the new article.')
@click.option('--markup', '-m', default='md', type=click.Choice(['md','rst','html']),
              help='Markup format to use for the note.')
def newnote(date, title, markup):
    check_if_loaded(cur_notebook)
    path = cur_notebook.newnote(date,title,markup)
    click.launch(path)


@cli.command(help='Creates a new appendix in the currently loaded '
                  'notebook, with name TITLE.')
@click.argument('title', type=click.STRING)
@click.option('--markup', '-m', default='md', type=click.Choice(['md','rst','html']),
              help='Markup format to use for the note.')
def newappendix(title, markup):
    check_if_loaded(cur_notebook)
    cur_notebook.newpage(title, markup)


@cli.command(help='If a note exists for today in the currently loaded '
                  'notebook and a PDF version exists, open it. If the '
                  'PDF does not exist, then the PDF will be created '
                  'and then opened. If no note for today exists, then '
                  'Scribbler will offer to create it for you.')
def today():
    click.secho('Not yet implemented.', fg='red', bold=True)


@cli.command(help='Launches the currently loaded notebook\'s directory '
                  'in a file browser.')
def cd():
    check_if_loaded(cur_notebook)
    click.launch(cur_notebook.location)


def add_file(method, src, dest, nb=cur_notebook, force=False):
    """
    A function for copying/linking/symlinking a file into a notebook.
    It will pass SRC and DEST to METHOD, acting on notebook NB. In the
    event that the file already exists then it will prompt for an
    action. If FORCE is specified and True then files will be 
    overwritten without asking permission first.
    """
    def newpath(name):
        """
        Computes what the new path within the notebook would be for
        that name.
        """
        return os.path.join(os.path.dirname(nb.get_destination(src, dest)), newname)

    try:
        method(nb, src, dest, force)
    except OSError:
        if click.confirm('Placing this file in the notebook would '
                         'overwrite an existing file. Continue?'):
            method(nb, src, dest, overwrite=True)
        else:
            newname = os.basename(nb.get_destination(src, dest))
            fname, ext = os.path.splitext(newname)
            testname = newname
            count = 0
            while os.isfile(newpath(testname)):
                count += 1
                testname = fname + '-' + str(count) + ext
            newname = testname
            newname = click.confirm('Provide a new filename ("-" '
                                    'indicates that the file should '
                                    'not be copied)', default=newname)
            if newname == '-':
                return
            else:
                add_file(method, src, newpath(newname), nb)
