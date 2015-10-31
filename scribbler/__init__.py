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
from .errors import ScribblerWarning, ScribblerError

__appname__    = "scribbler"
__author__     = "Chris MacMackin"
__maintainer__ = "Chris MacMackin"
__license__    = "GPLv3"
__status__     = "Beta"
__version__    = '0.2.0'

dt = datetime.datetime.now()
scribbler = ScribblerDatabase(click.get_app_dir(__appname__))
cur_notebook = scribbler.current()

ERROR = click.style('ERROR: ', fg='red', bold=True)

def check_if_loaded(notebook):
    """
    Raise an error message if no notebook is loaded.
    """
    if not isinstance(notebook,Notebook):
        click.echo(ERROR + 'Can not perform this operation because no notebook is loaded.')
        click.echo('Load a notebook with `scribbler load <notebook name>`')
        sys.exit(1)


@click.group()
@click.version_option(version=__version__)
def cli():
    warnings.simplefilter('always', ScribblerWarning)


@cli.command(help='Copies SRC to the appropriate location within the '
                  'files directory of your notebook. Unless '
                  'the `-d/--destination` flag is used, files will be '
                  'placed in the directory corresponding to their file '
                  'type, as specified in the notebook\'s YAML file.')
@click.argument('src', type=click.Path(exists=True))
@click.option('-d','--destination', type=click.Path(),
              help='Destination, relative to the root of the notebook '
                   'files directory, to which SRC is copied.')
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


@cli.command(help='Creates a hard link to SRC in the files directory '
                  'of your notebook. Unless the `-d/--destination` '
                  'flag is used, links will be placed in the directory '
                  'corresponding to their file type, as specified in '
                  'the notebook\'s YAML file.')
@click.argument('src', type=click.Path(exists=True))
@click.option('-d','--destination', type=click.Path(),
              help='Destination, relative to the root of the notebook '
                   'files directory, for the link to be placed.')
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


@cli.command(help='Creates a symlink to SRC. Unless the '
                  '`-d/--destination`  flag is used, links will be '
                  'placed in the directory corresponding to their file '
                  'type, as specified in the notebook\'s YAML file.')
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
@click.argument('location', type=click.Path())
def init(name, location):
    try:
        scribbler.add(name, location)
    except ScribblerError as e:
        click.echo(ERROR + str(e))


@cli.command(help='Remove notebook NAME from Scribbler\'s records.')
@click.argument('name', type=click.STRING)
@click.confirmation_option(help='Are you sure you want to forget this '
                                'notebook?')
@click.option('--delete/--no-delete', default=False,
              help='Delete the contents of the notebook. Default: no-delete')
def forget(name, delete):
    try:
        scribbler.delete(name, delete)
    except ScribblerError as e:
        click.echo(ERROR + str(e))


@cli.command(help='Load notebook NAME, meaning that Scribbler '
                  'operations will act on it.')
@click.argument('name', type=click.STRING)
def load(name):
    try:
        scribbler.load(name)
    except ScribblerError as e:
        click.echo(ERROR + str(e))


@cli.command(help='Unload the currently loaded notebook from '
                  'Scribbler. Scribbler commands will no longer work '
                  'on a notebook.')
def unload():
    scribbler.unload()


@cli.command(help='Lists all notebooks known to Scribbler.')
def notebooks():
    click.echo('The following notebooks are known to Scribbler:\n')
    form = '    {:24}  {}'
    for nb in scribbler:
        click.echo(form.format(nb.name, nb.location))

    
@cli.command(help='Creates the HTML and PDF output of the currently '
                  'loaded notebook.')
def build():
    check_if_loaded(cur_notebook)
    try:
        cur_notebook.build()
    except ScribblerError as e:
        click.echo(ERROR + str(e))
    scribbler.save(cur_notebook)


@cli.command(help='Creates a new note or appendix in the currently '
                  'loaded notebook.')
@click.option('--date', '-d', default=dt.strftime('%Y-%m-%d %H:%M'),
              help='Date to use for the new note, in format "YYYY-MM-DD HH:mm". '
                   'Default: today\'s date.')
@click.option('--title', '-t', default=dt.strftime('%A'),
              help='Title of the new note/appendix. Default: current day of week.')
@click.option('--markup', '-m', default='md', type=click.Choice(['md','rst','html']),
              help='Markup format to use for the note. Default: md.')
@click.option('--note/--appendix', default=True,
              help='Whether to create a note or an appendix. Default: note.')
def new(date, title, markup, note):
    check_if_loaded(cur_notebook)
    try:
        if note:
            path = cur_notebook.newnote(date,title,markup)
        else:
            path = cur_notebook.newpage(title, markup)
    except ScribblerError as e:
        click.echo(ERROR + str(e))
        sys.exit(1)
    scribbler.save(cur_notebook)
    click.launch(path)


@cli.command(help='Registers an existing file at PATH as a note or '
                  'appendix.')
@click.argument('path', type=click.Path(exists=True))
@click.option('--title', '-t', default=dt.strftime('%A'),
              help='Title of the note/appendix. Default: current day of week.')
@click.option('--date', '-d', default=dt.strftime('%Y-%m-%d %H:%M'),
              help='Date to use for the new note, in format "YYYY-MM-DD HH:mm". '
                   'Default: today\'s date.')
@click.option('--overwrite/--no-overwrite', default=False,
              help='Overwrite an existing record for this file. '
                   'Default: no-overwrite.')
@click.option('--note/--appendix', default=True,
              help='Whether to create a note or an appendix. Default: note.')
def add(path, title, overwrite, note):
    check_if_loaded(cur_notebook)
    try:
        if note:
            cur_notebook.addnote(date,title,path,overwrite)
        else:
            cur_notebook.addpage(title,path,overwrite)
    except ScribblerError as e:
        click.echo(ERROR + str(e))
        sys.exit(1)
    scribbler.save(cur_notebook)


@cli.command(help='Opens the source file(s) for note(s) with date or '
                  'title corresponding to IDENT.')
@click.argument('ident', type=click.STRING)
@click.option('--date/--title', default=True,
              help='Whether IDENT is the date or title to search for. Default: date.')
@click.option('--note/--appendix', default=True,
              help='Whether searches for a note or an appendix '
                   'matching IDENT. Default: note.')
def src(ident, date, notes):
    check_if_loaded(cur_notebook)
    note_files = note_from_ident(ident, date, notes)
    if len(note_files) == 0:
        click.echo('No matches found.')
        sys.exit(1)
    for n in note_files:
        click.launch(os.path.join(cur_notebook.location, n.src_path))


@cli.command(help='Opens the HTML file(s) for note(s) with date or '
                  'title corresponding to IDENT. If HTML version does '
                  'not exist, then will build it.')
@click.argument('ident', type=click.STRING)
@click.option('--date/--title', default=True,
              help='Whether IDENT is the date or title to search for. Default: date.')
@click.option('--note/--appendix', default=True,
              help='Whether searches for a note or an appendix '
                   'matching IDENT. Default: note.')
def html(ident, date, notes):
    check_if_loaded(cur_notebook)
    note_files = note_from_ident(ident, date, notes)
    if len(note_files) == 0:
        click.echo('No matches found.')
        sys.exit(1)
    rebuild = False
    for n in note_files:
        rebuild = rebuild or not n.html_path
    if rebuild:
        try:
            cur_notebook.build()
        except ScribblerError as e:
            click.echo(ERROR + str(e))
            sys.exit(1)
        note_files = note_from_ident(ident, date, notes)
    for n in note_files:
        click.launch(os.path.join(cur_notebook.location, n.html_path))


@cli.command(help='Opens the PDF file(s) for note(s) with date or '
                  'title corresponding to IDENT.')
@click.argument('ident', type=click.STRING)
@click.option('--date/--title', default=True,
              help='Whether IDENT is the date or title to search for. Default: date.')
@click.option('--note/--appendix', default=True,
              help='Whether searches for a note or an appendix '
                   'matching IDENT. Default: note.')
def pdf(ident, date, notes):
    check_if_loaded(cur_notebook)
    note_files = note_from_ident(ident, date, notes)
    if len(note_files) == 0:
        click.echo('No matches found.')
        sys.exit(1)
    rebuild = False
    for n in note_files:
        try:
            rebuild = rebuild or not n.pdf_path
        except ScribblerError as e:
            click.echo(ERROR + str(e))
            sys.exit(1)
    if rebuild:
        cur_notebook.build()
        note_files = note_from_ident(ident, date, notes)
    for n in note_files:
        click.launch(os.path.join(cur_notebook.location, n.pdf_path))

@cli.command(help='Opens the YAML file containing the notebook\'s settings.')
def settings():
    check_if_loaded(cur_notebook)
    click.launch(os.path.join(cur_notebook.location, cur_notebook.SETTINGS_FILE))

@cli.command(help='Launches the currently loaded notebook\'s directory '
                  'in a file browser.')
def cd():
    check_if_loaded(cur_notebook)
    click.launch(cur_notebook.location)


@cli.command(help='Lists the contents of the currently loaded notebook.')
def list():
    check_if_loaded(cur_notebook)
    click.echo('Notebook: ' + cur_notebook.name)
    click.echo('Location: ' + cur_notebook.location)
    click.echo()
    if len(cur_notebook.notes) == 0:
        numnotes = 'Contains no notes.'
    elif len(cur_notebook.notes) == 1:
        numnotes = 'Contains 1 note:'
    else:
        numnotes = 'Contains {} notes:'.format(len(cur_notebook.notes))
    click.echo(numnotes)
    for note in sorted(cur_notebook.notes.values(), key=lambda n: n.slug):
        click.echo('    {:10}  {:22}  {}'.format(note.date, note.name, note.src_path))
    click.echo()
    if len(cur_notebook.appendices) == 0:
        numappe = 'Contains no appendices.'
    elif len(cur_notebook.appendices) == 1:
        numappe = 'Contains 1 appendix:'
    else:
        numappe = 'Contains {} appendices:'.format(len(cur_notebook.appendices))
    click.echo(numappe)
    for appe in sorted(cur_notebook.appendices.values(), key=lambda a: a.slug):
        click.echo('    {:22}  {}'.format(appe.name, appe.src_path))


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
            method(nb, src, dest, True)
        else:
            newname = os.path.basename(nb.get_destination(src, dest))
            fname, ext = os.path.splitext(newname)
            testname = newname
            count = 0
            while os.path.isfile(newpath(testname)):
                count += 1
                testname = fname + '-' + str(count) + ext
                if count > 3: raise Exception()
            newname = testname
            newname = click.prompt('Provide a new filename ("-" '
                                   'to not copy)', default=newname)
            if newname == '-':
                return
            else:
                add_file(method, src, newpath(newname), nb)

def note_from_ident(ident, date=True, notes=True):
    """
    Iterates through notes and returns a list of any matching IDENT.
    If DATE is True then IDENT must match the date. Otherwise, IDENT
    must match the title. If NOTES is False then will search them
    instead and IDENT is assumed to be the title.
    """
    check_if_loaded(cur_notebook)
    note_files = []
    if date:
        m = 'date'
    else:
        m = 'name'
    if not notes:
        for appe in cur_notebook.appendices.values():
            if appe.name == ident: note_files.append(appe)
    else:
        for note in cur_notebook.notes.values():
            if getattr(note, m) == ident: note_files.append(note)
    return note_files
