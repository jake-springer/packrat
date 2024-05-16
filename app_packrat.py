#!/usr/bin/python3

#------------------------------------------------------------------------------
''' 
packrat v2
Jacob Springer
5/14/24
Utility for managing tar archives on linux systems. This is the TUI application
the user interfaces with. 
'''
#------------------------------------------------------------------------------

from rich.console import Console 
from rich.table import Table 
from packrat import PackRat
import sys
import os

#------------------------------------------------------------------------------

tag = "[blue]packrat >[/]"
console = Console()

#------------------------------------------------------------------------------
# Tables & Menus

def help_table():
    table = Table()
    table.add_column("Command")
    table.add_column("Description")
    table.add_row("pack", "{all/here/ID} - backup a targeted directory")
    table.add_row("-h / --help", "Display this table")
    table.add_row("-l / --list", "List all targets and their ID's in the target directories file")
    table.add_row("-a / --add {path}", "Add path to the target directories file")
    table.add_row("-d / --del {target ID}", "Remove a target by it's ID in the list")
    # table.add_row("-bd / --backups_dir", "Change where backups are stored in the file system")
    console.print(table)

def list_table():
    # List all the possible targets saved in the config
    table = Table()
    table.add_column("ID")
    table.add_column("Target")
    i = 1
    for d in packrat.targets:
        table.add_row(str(i), d)
        i += 1 
    console.print(table)

#------------------------------------------------------------------------------

def eval_args(args):
    if not args:
        report("please provide a command to use with packrat")
        report('hint: use "--help" for more information')
    elif args[0] in ('-h', '--help'):
        help_table()
    elif args[0] in ('-l', '--list'):
        list_table()
    # Add new target directory
    elif args[0] in ('-a', '--add'):
        try:
            target_path = args[1]
            target_path = resolve_path(target_path)
            result = packrat.add_target(target_path)
            packrat.save_config()
            if result == True:
                report("added path successfully")
            else:
                report("failed adding path")
        except IndexError:
            report('missing directory path')
    elif args[0] in ('-d', '--del'):
        try:
            target_id = args[1]
            remove_by_id(target_id)
        except IndexError:
            report('missing target ID')
            report('use "--list" to see all target IDs')
    # Pack target directory
    elif args[0] in ('pack'):
        try:
            operator = args[1]
        except IndexError:
            report("provide an operator to use with pack")
            report('use "--help" for more information')
        if operator == 'all':
            pack_all()
        elif operator == 'id':
            try:
                id_arg = args[2]
            except IndexError:
                report(f'no target with ID "{str(id_arg)}"')
                return 
            pack_by_index(id_arg)
        elif operator == 'here':
            path = os.getcwd()
            pack_by_path(path)
            return             
        else:
            report(f'unknown operator "{str(operator)}"')
            report(f'use "all", "id", or "path"')



def report(msg):
    console.print(f"{tag} {msg}")


def resolve_path(path) -> str:
    # Resolve an ambiguous path
    if path == '.':
        p = os.getcwd()
    elif path[0:1] == '~/':
        p = os.path.expanduser(path)
    elif not os.path.isabs(path):
        p = os.path.join(os.getcwd(), path)
    else:
        p = path
    if not os.path.exists(p):
        report(f"directory not found: {p}")
        return None 
    return p 


def update_backups_dir(self, path):
    rp = resolve_path(path)
    if not rp: return 
    packrat.settings['backups_dir'] = p 
    packrat.save_config()
    report(f"updated backups directory to {rp}")

def pack_by_path(target_path):
    report(f'packing {target_path} > {backups_dir}')
    result = packrat.pack_by_path(target_path)
    if not result:
        report(f'error packing "{target_path}"')
        return 
    else:
        report(f'completed')

    
    
def pack_by_index(target_id: int):
    try:
        target_index = int(target_id) - 1
        target_name = packrat.targets[target_index]
    except ValueError:
        report(f'error packing ID "{str(target_id)}"')
        report('use "--list" to see all target IDs')
    except IndexError:
        report(f'error packing ID "{str(target_id)}"')
        report('use "--list" to see all target IDs')
    report(f"packing target: {target_name}")
    result = packrat.pack_by_index(target_index)
    if not result:
        report(f'error packing ID "{str(target_id)}"')
        report('use "--list" to see all target IDs')

def pack_all():
    if not packrat.targets:
        report(f"no directories flagged for archive")
        report('use "--help" for information on flagging directories')
        return 
    for target in packrat.targets:
        destination = packrat.generate_tarfile_name(target)
        report(f'backing up {target} > {destination}')
        packrat.pack_by_path(target)

def remove_by_id(target_id: int):
    try:
        target_index = int(target_id) - 1
        target_name = packrat.targets[target_index]
        result = packrat.remove_target(target_index)
        if not result:
            report(f'error removing directory by ID "{str(target_id)}"')
        else:
            report(f"removed {target_name}")
            packrat.save_config()
    except ValueError:
        report(f'error removing directory by ID "{str(target_id)}"')
    except IndexError:
        report(f'error removing directory by ID "{str(target_id)}"')

packrat = PackRat()
backups_dir = packrat.settings['backups_dir']
args = sys.argv[1:]
eval_args(args)
