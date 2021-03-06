# Copyright 2014-2015 Allen Institute for Brain Science
# This file is part of Allen SDK.
#
# Allen SDK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Allen SDK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Allen SDK.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import logging

class Manifest(object):
    """Manages the location of external files 
     referenced in an Allen SDK configuration """

    DIR = 'dir'
    FILE = 'file'
    DIRNAME = 'dir_name'
    log = logging.getLogger(__name__)

    def __init__(self, config=None, relative_base_dir='.'):
        self.path_info = {}
        self.relative_base_dir = relative_base_dir

        if config != None:
            self.load_config(config)
       
        
    def load_config(self, config):
        ''' Load paths into the manifest from an Allen SDK config section.
        
        Parameters
        ----------
        config : Config
            Manifest section of an Allen SDK config.
        '''
        for path_info in config:
            path_type = path_info['type']
            path_format = None
            if 'format' in path_info:
                path_format = path_info['format']
            
            if path_type == 'file':
                try:
                    parent_key = path_info['parent_key']
                except:
                    parent_key = None
                
                self.add_file(path_info['key'],
                              path_info['spec'],
                              parent_key,
                              path_format)
            elif path_type == 'dir':
                try:
                    parent_key = path_info['parent_key']
                except:
                    parent_key = None
                
                spec = path_info['spec']
                absolute = False
                if spec[0] == '/':
                    absolute = True
                self.add_path(path_info['key'],
                              path_info['spec'],
                              path_type,
                              absolute,
                              path_format,
                              parent_key)
            else:
                Manifest.log.warning("Unknown path type in manifest: %s" %
                                     (path_type))
                        
        
    def add_path(self, key, path, path_type=DIR,
                 absolute=True, path_format=None, parent_key=None):
        '''Insert a new entry.
        
        Parameters
        ----------
        key : string
            Identifier for referencing the entry.
        path : string
            Specification for a path using %s, %d style substitution.
        path_type : string enumeration
            'dir' (default) or 'file'
        absolute : boolean
            Is the spec relative to the process current directory.
        path_format : string, optional
            Indicate a known file type for further parsing.
        parent_key : string
            Refer to another entry.
        '''
        if parent_key:
            path_args = []
            
            try:
                parent_path = self.path_info[parent_key]['spec']
                path_args.append(parent_path)
            except:
                Manifest.log.error("cannot resolve directory key %s" % (parent_key))
                raise
            path_args.extend(path.split('/'))
            path = os.path.join(*path_args)
        
        # TODO: relative paths need to be considered better
        if absolute == True:
            path = os.path.abspath(path)
        else:
            path = os.path.abspath(os.path.join(self.relative_base_dir, path))
            
        if path_type == Manifest.DIRNAME:
            path = os.path.dirname(path)
            
        self.path_info[key] = { 'type': path_type,
                                'spec': path}
        
        if path_type == Manifest.FILE and path_format != None:
            self.path_info[key]['format'] = path_format


    def add_paths(self, path_info):
        ''' add information about paths stored in the manifest.
        
        Parameters
            path_info : dict
                Information about the new paths
        '''
        for path_key, path_data in path_info.items():
            path_format = None
            
            if 'format' in path_data:
                path_format = path_data['format']
            
            Manifest.log.info("Adding path.  type: %s, format: %s, spec: %s" %
                              (path_data['type'],
                               path_data['spec'],
                               path_format))
            entry = { 'type': path_data['type'],
                      'spec': path_data['spec'] 
                    }
            if path_format != None:
                entry['format'] = path_format

            self.path_info[path_key] = entry
    
    
    def add_file(self,
                 file_key,
                 file_name,
                 dir_key=None,
                 path_format=None):
        '''Insert a new file entry.
        
        Parameters
        ----------
        file_key : string
            Reference to the entry.
        file_name : string
            Subtitutions of the %s, %d style allowed.
        dir_key : string
            Reference to the parent directory entry.
        path_format : string, optional
            File type for further parsing.
        '''
        path_args = []
        
        if dir_key:
            try:
                dir_path = self.path_info[dir_key]['spec']
                path_args.append(dir_path)
            except:
                Manifest.log.error("cannot resolve directory key %s" % (dir_key))
                raise
        elif not file_name.startswith('/'):
            path_args.append(os.curdir)
        else:
            path_args.append(os.path.sep)
        
        path_args.extend(file_name.split('/'))
        file_path = os.path.join(*path_args)
        
        self.path_info[file_key] = { 'type': Manifest.FILE,
                                     'spec': file_path }
        
        if path_format:
            self.path_info[file_key]['format'] = path_format
    
    
    def get_path(self, path_key, *args):
        '''Retrieve an entry with substitutions.
        
        Parameters
        ----------
        path_key : string
            Refer to the entry to retrieve.
        args : any types, optional
           arguments to be substituted into the path spec for %s, %d, etc.
        
        Returns
        -------
        string
            Path with parent structure and substitutions applied.
        '''
        path_spec = str(self.path_info[path_key]['spec'].encode('ascii', 'ignore'))

        if args != None and len(args) != 0:
            path = path_spec % args
        else:
            path = path_spec
            
        return path
    
    
    def get_format(self, path_key):
        '''Retrieve the type of a path entry.
        
        Parameters
        ----------
        path_key : string
            reference to the entry
        
        Returns
        -------
        string
            File type.
        '''
        path_entry = self.path_info[path_key]
        path_format = None
        
        if 'format' in path_entry:
            path_format = path_entry['format']
            
        return path_format
    
    
    def create_dir(self, path_key):
        '''Make a directory for an entry.
        
        Parameters
        ----------
        path_key : string
            Reference to the entry.
        '''
        dir_path = self.get_path(path_key)
        
        try:
            os.stat(dir_path)
        except:
            os.mkdir(dir_path)
    
    
    def check_dir(self, path_key, do_exit=False):
        '''Verify a directories existence or optionally exit.
        
        Parameters
        ----------
        path_key : string
            Reference to the entry.
        do_exit : boolean
            What to do if the directory is not present.
        '''
        dir_path = self.get_path(path_key)
        
        if not os.path.exists(dir_path):
            Manifest.log.fatal('Directory %s does not exist; exiting.' % 
                               (dir_path))
            if do_exit == True:
                quit()
    
    def resolve_paths(self, description_dict, suffix='_key'):
        '''Walk input items and expand those that refer to a manifest entry.
        
        Parameters
        ----------
        description_dict : dict
            Any entries with key names ending in suffix will be expanded.
        suffix : string
            Indicates the entries to be expanded.
        '''
        key_pattern =  re.compile('(.*)%s$' % (suffix))
        
        for description_key, manifest_key in description_dict.items():
            m = key_pattern.match(description_key)
            if m:
                real_key = m.group(1)  # i.e. job_dir_key -> job_dir
                filename = self.get_path(manifest_key)
                description_dict[real_key] = filename
                del description_dict[description_key]
