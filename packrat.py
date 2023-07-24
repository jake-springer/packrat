#!/usr/bin/python

#----------------------------------------------------------

import json
import tarfile
import os 
import sys
from datetime import datetime 
from subprocess import call

#----------------------------------------------------------

app_title = "Pack Rat"
app_version = "0.2.4"
data_file = os.path.expanduser("~/.config/packrat.json")
cli_args = sys.argv[1:]
line_length = 50
options = {
    "verbose":False
}

quit_terms = ["exit", "q","quit", "end"]

#----------------------------------------------------------

default_data = {
        "settings":{
            "drop_dir":None,
            "use_default_target":True
            },   
        "sets":[]
        }


def no_data():
    '''~/.config/packrat.json not found'''
    print(f"\n[!] Could not load data file --> {data_file} \n")
    print("What do you want to do?")
    print()
    print("[1]. Create new file")
    print("[2]. Exit")
    while True:
        select = input("\n[?] ")
        if select == '2':
            sys.exit()
        elif select == '1':
            with open(data_file, 'w') as file:
                file.write(json.dumps(default_data, indent=4))
            print("new file created ->", data_file)
            break


def load_data():
    validate_config()
    with open(data_file, 'r') as file:
        return json.load(file)


def save_data(data):
    with open(data_file, 'w') as file:
        file.write(json.dumps(data, indent=4))


def validate_config():
    try:
        with open(data_file, 'r') as file:
            pass 
    except FileNotFoundError:
       no_data() 

#---------------------------------------------------------

def get_now(): # returns date,time
    now = datetime.now()
    d = now.strftime("%m-%d-%y")
    t = now.strftime("%H:%M")
    return d, t


def date_in_string(string):
    date = get_now()[0]
    return string.replace("%", date)


def clear():
    call("clear")


def header(text):
    print(''' 
____            _      ____       _   
|  _ \ __ _  ___| | __ |  _ \ __ _| |_ 
| |_) / _` |/ __| |/ / | |_) / _` | __|
|  __/ (_| | (__|   <  |  _ < (_| | |_ 
|_|   \__,_|\___|_|\_\ |_| \_\__,_|\__|                                        
    ''')
    print("Version:", app_version)
    

class Error:
    def __init__(self, desc, code, fatal=False, verbose=True):
        self.desc = desc
        self.code = str(code)

        error_string = f"packrat {self.code.lower()}: {desc} "
        if fatal:
            error_string += " (CRITICAL)"
            if verbose:
                print(error_string)
            sys.exit()    
        if verbose:
            # error_string += "\n"
            print(error_string)
 

def quick_look():
    data = load_data()
    set_list = data["sets"]
    settings = data["settings"]
    
    set_count = str(len(set_list))
    drop_dir = settings["drop_dir"]

    print("[>] drop directory    ->  ", drop_dir)
    print("[>] number of sets    ->  ", set_count)

#---------------------------------------------------------

help_info = {
    "set":{
        "add":{
            "example":"set add {set name} {path to add}",
            "desc":"add a new path for the set to archive."
        },
        "target":{
            "example":"set target {set name} {path to archive.tar.gz}",
            "desc":"specify the path and filename of the archive."
        },
        "info":{
            "example":"set info {set name}",
            "desc":"get detailed information about a set"
        },
        "list":{
            "example":"set list",
            "desc":"show a list of all sets."
        },
        "delete":{
            "example":"set delete {set name}",
            "desc":"delete a saved set."
        },
        "new":{
            "example":"set new {set name}",
            "desc":"create a new set"
        }
    }
}


def display_help_page(section):
    commands = help_info[section]
    print(f"\n  --->  \"{section}\" help page  <---")
    for action in commands:
        command_info = help_info[section][action]
        print()
        print("->", action)
        print("--->", command_info["desc"])
        print("---> example:", command_info["example"])
    print()
    

def help_handler(category=None):
    print()
    if category:
        try:
            section = help_info[category]
        except KeyError:
            Error(f"No help section for {category}", 106)
            return 
        display_help_page(category)
    
    else:
        for command in help_info:
            display_help_page(command)

#--------------------------------------------------------
#   ===  SETS ===

def add_record(set_dict, record):
    date, time = get_now()
    text = f"[{date} | {time}] {record}"
    set_dict["records"].append(text)
    return set_dict


def find_set_index(set_list, set_name):
    for s in set_list:
        if s["name"].strip() == set_name.strip():
            return set_list.index(s)
    return -1

# finds the set dict in the json and returns it
def pull_set(set_name):
    data = load_data()
    sets = data["sets"]
    set_index = find_set_index(sets, set_name.strip())
    if set_index == -1: # "not set_index" means I can't access index 0
        Error(f"Could not find set --> {set_name}", 102)
        return
    return sets[set_index]


def save_set(set_dict): # NEW
     # finds the set dict in the json, updates it, and saves it
    data = load_data()
    sets = data["sets"]
    set_index = find_set_index(sets, set_dict["name"])
    if set_index == -1:
        Error(f"Set {set_dict['name']} was given to save, but it doesn't exist.", 103)
        return
    sets[set_index] = set_dict
    save_data(data)
    # print(f"[!] Set \"{set_dict['name']}\" was updated\n")

# adds path to a sets "path":[] value
def add_directory(set_name, dir_path):
    if dir_path[0] == "~":
        dir_path = os.path.expanduser(dir_path)
    target_set = pull_set(set_name)
    if not target_set:
        Error(f"Set \"{set_name}\" not found.", 102, fatal=True, verbose=False)
    if not os.path.exists(dir_path):
        Error(f"Path \"{dir_path}\" does not exist.", 101)
    target_set["paths"].append(dir_path)
    save_set(target_set)
    print(f"[~] Path added to set \"{set_name}\" -> {dir_path}")

# validates the abspath of the tar file being set
def validate_path(test_path):
    path = os.path.split(test_path)
    if not os.path.exists(path[0]):
        return 0 
    return 1


def default_target(set_name):
    data = load_data()
    drop_dir = data["settings"]["drop_dir"]
    # set drop dir to ~/ if not set  
    if not drop_dir:
        Error("cannot set default target -> no drop directory configured.", 555)
        print("defaulting to the home directory")
        drop_dir = os.path.expanduser("~/")

    tarfile = f"{set_name.lower()}_%.tar.gz"
    return os.path.join(drop_dir, tarfile)


def set_tarfile_path(set_name, new_tar):
    if new_tar[0] == '~':
        new_tar = os.path.expanduser(new_tar)
    target_set = pull_set(set_name)
    if not validate_path(new_tar):
        print(f"[!] Path error. Directory doesn't exist.\n")
        return
    old_tar = target_set["tar_file"]
    target_set["tar_file"] = new_tar
    record = f"changed tarfile: {old_tar} -> {new_tar}"
    target_set = add_record(target_set, record)
    save_set(target_set)
    print(f"[~] Set tar path for \"{set_name}\" -> {new_tar}\n")


def create_set(set_name):
    data = load_data()
    set_list = data["sets"]

    # check if set with matching name exists
    for s in set_list:
        if s["name"].lower() == set_name:
            Error(f"Set with name \"{set_name}\" already exists.", 107)
            return

    # pull settings
    config = data["settings"]
    use_default_target = config["use_default_target"]
    if use_default_target:
        print("> \"use default target\" enabled")
        target_dir = default_target(set_name)
        if default_target:
            print("-> set default target:", target_dir)
        else:
            print("[!] no drop directory specified, defaulted to home directory:", target_dir)
    else:
        print("> \"use default target\" disabled")
        target_dir = None

    # create set dictionary
    new_set = {
        "name":set_name,
        "tar_file":target_dir,
        "last_ran":None,
        "paths":[],
        "records":[]
    }

    # save the set to the db
    new_set = add_record(new_set, "set created")
    set_list.append(new_set)  
    save_data(data)
    print("[~] Created new set: " + set_name + "\n")


def delete_set(set_name):
    data = load_data()
    sets = data["sets"]
    set_index = find_set_index(sets, set_name.strip())
    if set_index == -1: # "not set_index" means I can't access index 0
        print(f"[!] Could not find set \"{set_name}\"\n")
        return
    print(f"[!] Delete the \"{set_name}\" set?")
    conf = input("(y/N): ")
    if conf.lower() != 'y':
        print("[!] Cancelled, set preserved.\n")
        return
    sets.remove(sets[set_index])
    save_data(data)
    print(f"[!] Set \"{set_name}\" removed.\n")


def list_sets():
    data = load_data()
    sets = data["sets"]
    print()
    print('-' * 40)
    for s in sets:
        print()
        print("[>] Set name:", s["name"])
        if not s["tar_file"]:
            print("--> no save file set")
        else:
            print("--> Save file:", s["tar_file"])
        if not s["paths"]:
            print("--> No paths added to the set.")
        else:
            print("--> Added paths:", len(s["paths"]))
    print()
    print('-' * 40)
    print()


def set_info(set_name):
    print()
    t_set = pull_set(set_name)
    name = t_set['name']
    tar = t_set["tar_file"]
    last_ran = t_set["last_ran"]
    path_list = t_set["paths"]
    records = t_set["records"] #wip
    print("->", name)
    if tar:
        print("--->", tar)
    else:
        print("---> no tarfile specified")

    if last_ran:
        print("---> last:", last_ran)
    else:
        print("---> never ran")

    if path_list:
        for p in path_list:
            print("------>", p)
    else:
        print("---> no paths added")

    print()

#! is different from add_directory() how???
def set_add_path(set_name, path):
    target_set = pull_set(set_name)
    # make sure path exists
    if not os.path.exists(path):
        print(f"[!] Path doesn't exist: {path}\n")
        return
    # add path to sets path registry
    target_set["paths"].append(path)
    target_set = add_record(target_set, f"added path: {path}")
    save_set(target_set)
    print(f"[~] Path added to {set_name} -> {path}\n")
    

def manage_sets(command_list):
    try:
        command = command_list[0]
    except IndexError:
        print("[!] Specify an option to use with \"set\" (eg: set info my_set)\n")
        return
    # no options
    if command == "list":
        list_sets()
        return
    elif command == "help":
        help_handler("set")
        return

    # single option
    try:
        option1 = command_list[1]
    except IndexError:
        Error(f"Not enough options provided for \"{command}\"", 105)
        try:
            print("Example:",help_info["set"][command]["example"], "\n")
        except KeyError:
            pass
        return
    
    if command == "new":
        create_set(option1)
        return

    elif command == "delete":
        delete_set(option1)
        return

    elif command == "info":
        set_info(option1)
        return
    
    elif command == "run":
        run(option1)
        return
    
    # two options    
    try:
        option2 = command_list[2]
    except IndexError:
        Error(f"Not enough options provided for \"{command}\"", 105)
        try:
            print("Example:",help_info["set"][command]["example"], "\n")
        except KeyError:
            pass
        return

    if command == "target":
        set_tarfile_path(option1, option2) 
        return
    elif command == "add":        
        add_directory(option1, option2)
        return
    
#--------------------------------------------------------

def archive_check(set_dict):
    has_tar = bool(set_dict["tar_file"])
    has_paths = bool(set_dict["paths"])
    if not has_tar or not has_paths:
        print(f"[!] Tar file -->  {str(has_tar).upper()}")
        print(f"[!] Paths    -->  {str(has_paths).upper()}")
        print(f"[!] Cannot begin archive of \"{set_dict['name']}\", missing requirements.")
        print()
        return False
    return True


def run(set_name):
    target_set = pull_set(set_name)
    if not archive_check(target_set):
        return
    print()
    print("-" * line_length)
    print()
    print(" ---> archive information <---\n")
    print("> Set name:", target_set["name"])
    print("> Tar file:", target_set["tar_file"])
    print("> Last archive:", target_set["last_ran"])
    print("> Paths:")
    for p in target_set["paths"]:
        print("->", p)
    print()
    print("-" * line_length)
    print()
    while True:
        conf = input("[?] Start archive (y/n): ")
        if conf.lower() == 'n':
            return
        elif conf.lower() == 'y':
            archive(target_set)
            return 


def archive(set_dict):
    date = get_now()[0]
    archive_name = set_dict["tar_file"]
    if "%" in archive_name:
        archive_name = date_in_string(archive_name)

    paths = set_dict["paths"]
    set_dict["last_ran"] = date

    print(f"-> Starting the \"{set_dict['name']}\" archive.")
    print("-> This may take a long time.\n")

    with tarfile.open(archive_name, "w:gz") as tarhandle:
        for path in paths:
            for root,dirs,files in os.walk(path):
                for f in files:
                    full_path = os.path.join(root, f)
                    print("--->", full_path)
                    tarhandle.add(full_path)
    
    set_dict["last_ran"] = date
    set_dict = add_record(set_dict, f"performed archive -> {archive_name}")
    save_set(set_dict)
    print("\n\n[!] Archive completed -> " + archive_name)
    print()

#--------------------------------------------------------
# admin functions

def reset_data():
    default_data = {
            "settings":{},
            "sets":[]
            }
    with open(data_file, 'w') as file:
        file.write(json.dumps(default_data, indent=4))
    create_set("main")


def add_data_field():
    data = load_data()
    sets = data["sets"]
    try:
        print()
        k = input("[?] Data key: ")
        v = input("[?] Default value: ")
        print()
    except KeyboardInterrupt:
        return
    for s in sets:
        s[k] = v 
    save_data(data)
    print(f"\n[!] Updated all sets: {str(k)} = {str(v)}\n")


def admin_mode():
    print("\n\n\n--> You are in admin mode! <--")
    print("\n[!] See the documentation for admin commands.")
    while True:
        command = input("\n[admin] ").strip()
        if command in quit_terms:
            break
        elif command == "reset":
            reset_data()
            print("[>] JSON data has been reset.")
        elif command == "add_field":
            add_data_field()

#--------------------------------------------------------
# drop dir

def set_drop_dir(drop_dir_path):
    '''set the settings:{drop_dir:""} value in the json file'''
    if drop_dir_path[0] == "~": #  expand path if ~/...
        drop_dir_path = os.path.expanduser(drop_dir_path)
    if not os.path.exists(drop_dir_path):
        Error("Path doesn't exist", 108)
        return
    data = load_data()
    data["settings"]["drop_dir"] = drop_dir_path
    save_data(data)
    print("[>] Set drop directory:", drop_dir_path, "\n")


def config_handler(option_list):
    '''gateway for config functions'''
    try:
        command = option_list[0]
    except IndexError:
        print("provide an option to use with 'config'.\n")
        return
    if command == 'drop':
        try:
            set_drop_dir(option_list[1])
        except IndexError:
            print("provide a path to set as the drop directory\n")
            return

#--------------------------------------------------------

def main():
    data = load_data()
    header(app_title)
    print("(type \"help\" for more information)\n")
    quick_look()
    print("\n\n")
    while True:
        select = input("[~] ").split()
        cursor = select[0]
        commands = select[1:]
        if cursor in quit_terms:
            sys.exit()        
        elif cursor == "help":
            help_handler()
        elif cursor == "set":
            manage_sets(commands)
        elif cursor == "config":
            config_handler(commands)
        elif cursor == "clear":
            clear()
            header(app_title)
        elif cursor == "admin":
            admin_mode()
            print("\n---> You have left admin mode <---\n\n")
        else:
            print(f"\n[>] Not a recognized option: \"{cursor}\". Enter \"help\" for more infomration.")

#---------------------------------------------------------
#   === CLI handling ===

def cli_handler(options):
    add_ops = ["-a", "--add"] # packrat -a {set} (1 option)
    list_ops = ["-l", "--list", "--sets"] # packrat -l (0 options)
    command = options[0]
    if command in add_ops:
        try: 
            set_name = options[1]
        except IndexError:
            Error(
                "Must provide a set name. Use \"packrat -l\" to view sets.", 
                104, 
                fatal=True # kills program
            )
        add_directory(set_name, os.getcwd())
    if command in list_ops:
        list_sets()
    
    sys.exit()

if cli_args:
    cli_handler(cli_args)

clear()
main()

#---------------------------------------------------------
