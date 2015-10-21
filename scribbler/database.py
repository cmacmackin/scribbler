#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  database.py
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
Contains a class representing Scribbler's database of notebook's for this
user.
"""

import os
import unicodedata
import warnings
from pickle import load
from shutil import rmtree

from pelican.utils import slugify

from .errors import ScribblerError, ScribblerWarning
from .notebook import Notebook

class ScribblerDatabase(object):
    """
    Contains the information about what notebooks are available to
    Scribbler and about which notebook is currently loaded. Loads this
    from the information contained within data_dir.
    """
    
    LOADED_NAME = '__loaded__.pkl'
    
    def __init__(self, data_dir):
        self.scribbler_dir = data_dir
        if not os.path.isdir(self.scribbler_dir):
            os.makedirs(self.scribbler_dir)
    
    @staticmethod
    def name_to_filename(name):
        """
        Converts a notebook name to the filename which would store the
        pickled notebook.
        """
        #~ name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
        #~ name = unicode(re.sub('[^\w\s-]', '', name).strip().lower())
        #~ name = re.sub('[-\s]+', '-', name) 
        return slugify(name) + '.pkl'
    
    def get(self, name):
        """
        Get the notebook object corresponding to the provided name.
        """
        try:
            infile = open(os.path.join(self.scribbler_dir,
                          self.name_to_filename(name)),'r')
        except IOError:
            raise ScribblerError('No notebook with name `{}`'.format(name))
        nb = load(infile)
        return nb
    
    def add(self, name, location):
        """
        Create a new notebook with the given name, in the given location
        and add it to the database.
        """
        for nb in self:
            if nb.name == name:
                raise ScribblerError('Notebook with name `{}` already exists'.format(name))
            if name_to_filename(nb.name) == name_to_filename(name):
                raise ScribblerError('Name `{}` too similar to that of existing notebook `{}`'.format(name, nb.name))
            if os.path.samefile(nb.location, location):
                raise ScribblerError('Notebook `{}` already exists at location {}'.format(nb.name, location)) 
        if os.path.isfile(location):
            raise ScribblerError('Location {} exists but is not a directory'.format(path))
        nb = Notebook(name, location)
        nb_file = open(os.path.join(self.scribbler_path, self.name_to_filename(name)), 'w')
        nb.save(nb_file)
    
    def delete(self, name, del_files=False):
        """
        Remove records of the named notebook. Also remove the files
        associated with it, if del_files is True.
        """
        nb = self.get(name)
        if self.is_current(name):
            self.unload()
        os.remove(os.path.join(self.scribbler_dir, self.name_to_filename(name)))
        if del_files:
            try:
                rmtree(nb.location)
            except:
                warnings.warn('Error occurred while removing files for '
                              'notebook `{}`'.format(name), ScribblerWarning)
    
    def load(self, name):
        """
        Loads the notebook with the provided name.
        """
        self.unload()
        try:
            os.symlink(os.path.join(self.scribbler_dir, self.name_to_filename(name)),
                       os.path.join(self.scribbler_dir, self.LOADED_NAME))
        except OSError:
            raise ScribblerError('No notebook with name `{}`'.format(name))
    
    def unload(self):
        """
        Unloads any currently loaded notebooks.
        """
        try:
            os.remove(os.path.join(self.scribbler_dir, self.LOADED_NAME))
        except OSError:
            pass
        
    def is_current(self, name):
        curpath = os.path.join(self.scribbler_dir, self.LOADED_NAME)
        namepath = os.path.join(self.scribbler_dir, self.name_to_filename(name))
        return (os.path.islink(curpath) and 
                os.path.realpath(curpath) == os.path.realpath(namepath))
    
    def current(self):
        """
        Returns the currently loaded notebook. If no notebook loaded, returns None.
        """
        try:
            infile = open(os.path.join(self.scribbler_dir,self.LOADED_NAME),'r')
        except IOError:
            return None
        nb = load(infile)
        return nb
    
    def save(self, nb):
        """
        Saves the notebook NB to the scribbler directory.
        """
        nb_file = open(os.path.join(self.scribbler_path, self.name_to_filename(nb.name)), 'w')
        nb.save(nb_file)
    
    def __iter__(self):
        """
        Returns an iterable of the notebooks in the database.
        """
        files = [f for f in os.listdir(self.scribbler_dir) if f != self.LOADED_NAME and f.endswith('.pkl')]
        files.sort()
        nb_list = []
        for f in files:
            with open(f,'r') as r:
                nb_list.append(load(r))        
        return iter(nb_list)
