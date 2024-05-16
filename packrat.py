#!/usr/bin/python3
#------------------------------------------------------------------------------
''' 
packrat v2
Jacob Springer
5/14/24
Utility for managing tar archives on linux systems. This is the backend
portion that is used by other applications that interact with the user.
'''
#------------------------------------------------------------------------------

import json 
import os
from datetime import datetime
from rich.console import Console
import sys
from subprocess import call 

#------------------------------------------------------------------------------
# Global variables

DEFAULT_CONFIG = {  #  Default dict used when creating a new packrat.json
    "settings": {"backups_dir": os.path.expanduser("~/")},
    "targets":[]
}
now = datetime.now()
date = now.strftime("%y-%m-%d")
tag = "[red]packrat >[/]"
console = Console()

#------------------------------------------------------------------------------

class PackRat:
    def __init__(self):
        self.config_file = '/home/jakers/packrat.json'
        self.targets = []   #  stored in config
        self.settings = {}  #  stored in config
        self.load_config()
    
    def create_new_config(self):
        with open(self.config_file, 'w') as file:
            file.write(json.dumps(DEFAULT_CONFIG, indent=4))
        
    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError: 
            console.print(f"{tag} [red]Error:[/] Couldn't find config file: " + self.config_file)
            console.print(f"{tag} I'll create an empty config file, but you'll have to add new target paths.")
            self.create_new_config()
            console.print(f"{tag} Aborting...")
            sys.exit()
        except json.decoder.JSONDecodeError: 
            console.print(f"{tag} [red]Error:[/] problem loading config file: {self.config_file}")
            console.print(f"{tag} Check the file, or delete it and I'll genereate an empty one.")
            sys.exit()
        self.targets = data['targets']
        self.settings = data['settings']

    def save_config(self):
        # Overwrite self.config_file with new values
        data = {"settings":self.settings, "targets":self.targets}
        with open(self.config_file, 'w') as file:
            file.write(json.dumps(data, indent=4))

    def remove_target(self, target_index: int) -> bool:
        # Returns bool dependent on if it was successful
        try:
            del self.targets[target_index]
            return True
        except IndexError:
            return False 

    def add_target(self, target_path) -> bool:
        # Returns bool dependent on if it was successful
        if os.path.exists(target_path):
            self.targets.append(target_path)
            return True 
        else:
            return False 

    def generate_tarfile_name(self, file_path) -> str:
        # Convert filename to file_date.tar.gz
        base = os.path.basename(file_path).lower()
        tf = base + '_' + date + '.tar.gz'
        return os.path.join(self.settings['backups_dir'], tf)
    
    def pack_by_index(self, target_index: int) -> bool:
        try:
            source = self.targets[target_index]
        except IndexError:
            return False
        if not os.path.exists(source):
            return False 
        destination = self.generate_tarfile_name(source)
        call(["tar", "-czf", destination, source])
        return True 

    def pack_by_path(self, path, tarfile_name=None) -> bool:
        if not os.path.exists(path):
            return False 
        if not tarfile_name: # Generate default archive name
            tarfile_name = self.generate_tarfile_name(path)
        else:
            tarfile_name = os.path.join(self.settings['backups_dir'], tarfile_name)
        call(["tar", "-czf", tarfile_name, path])
        return True
    
