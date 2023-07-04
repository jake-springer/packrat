#----------------------------------------------------------

import json
import tarfile
import os 
import sys
from datetime import datetime 
from subprocess import call

#----------------------------------------------------------

app_title = "Pack Rat"
data_file = "data.json"
cli_args = sys.argv[1:]
options = {
    "verbose":False
}

arguments = [
    {
        "name":"add",
        "args":["-a", "--add"],
        "desc": "adds the current directory to the save index."
    }
]

quit_terms = ["exit", "q","quit", "end"]

#----------------------------------------------------------

def load_data():
    with open(data_file, 'r') as file:
        return json.load(file)


def save_data(data):
    with open(data_file, 'w') as file:
        file.write(json.dumps(data, indent=4))


def clear():
    call("clear")


def header(text):
    print(f"\n{text}\n")
    
#---------------------------------------------------------

def find_set_index(set_list, set_name):
    for s in set_list:
        if s["name"].strip() == set_name.strip():
            return set_list.index(s)
    return -1


def add_directory(dir_path):
    if not os.path.exists(dir_path):
        raise FileNotFoundError("[!] Error 101: path doesn't exist.")
        sys.exit()
    data = load_data()
    data[current_set]["paths"].append(dir_path)
    print("saver: added " + dir_path + " to save paths.")
    save_data(data)


def run(set_name):
    data = load_data()
    sets = data["sets"]
    set_index = find_set_index(sets, set_name.strip())
    if set_index == -1: # "not set_index" means I can't access index 0
        print(f"[!] Could not find set \"{set_name}\"\n")
        return
    else:
        set_dict = sets[set_index]

    tarfile_path = set_dict["tar_file"]
    paths = set_dict["paths"]
    print(f"-> Starting the \"{set_dict['name']}\" archive.")
    print("-> This may take a long time.\n")
    with tarfile.open(archive_name, "w:gz") as tarhandle:
        for path in paths:
            for root,dirs,files in os.walk(path):
                for f in files:
                    full_path = os.path.join(root, f)
                    if options["verbose"]:
                        print(full_path)
                    tarfile.add(full_path)
#--------------------------------------------------------

def help_handler():
    print("\n")
    print("\t> About Sets < ")
    print("Sets are groups of file paths to be archived, with a preset file name.")
    print("These are useful for performing archives on groups spread around the file system.")
    print("\n> set new {set name} : add a new set")
    print("> set list : view all sets")
    print("> set view {set name} : view information about a specific set.")
    print("> set target {set name} {/path/to/target.tar.gz} : configure the save file for the archive.")
    print("> set active {set name} : change the active set. Paths added with the -a option will be saved to this set.")
    print("> set delete {set name} : delete the specified set name")
    print("> set add {set_name} {dir/to/archive}")
    print("\n\n")

#--------------------------------------------------------

def validate_path(test_path):
    path = os.path.split(test_path)
    if not os.path.exists(path[0]):
        return 0 
    return 1


def set_tarfile_path(set_name, tarfile_path):
    data = load_data()
    sets = data["sets"]
    set_index = find_set_index(sets, set_name.strip())
    if set_index == -1: # "not set_index" means I can't access index 0
        print(f"[!] Could not find set \"{set_name}\"\n")
        return

    if not validate_path(tarfile_path):
        print(f"[!] Path error. Directory doesn't exist.\n")
        return

    target_set = sets[set_index]
    target_set["tar_file"] = tarfile_path
    save_data(data)
    print(f"[~] Set tar path for \"{set_name}\" -> {tarfile_path}\n")


def create_set(set_name):
    data = load_data()
    set_list = data["sets"]
    new_set = {
        "name":set_name,
        "tar_file":None,
        "paths":[]
    }
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
        

def set_add_path(set_name, path):
    # make sure set exists
    data = load_data()
    sets = data["sets"]
    set_index = find_set_index(sets, set_name.strip())
    if set_index == -1: # "not set_index" means I can't access index 0
        print(f"[!] Could not find set \"{set_name}\"\n")
        return 
    target_set = sets[set_index]
    # make sure path exists
    if not os.path.exists(path):
        print(f"[!] Path doesn't exist: {path}\n")
        return
    # add path to sets path registry
    target_set["paths"].append(path)
    save_data(data)
    print(f"[~] Path added to {set_name} -> {path}\n")
    


def manage_sets(command_list):
    try:
        command = command_list[0]
        #option = command_list[1] need to change this for optionless commands
    except IndexError:
        print("[!] Specify an option to use with \"set\" (eg: set add my_set)\n")
        return

    if command == "new":
        option = command_list[1]
        create_set(option)
    elif command == "target":
        set_name = command_list[1]
        tarfile_path = command_list[2]
        set_tarfile_path(set_name, tarfile_path) 
    elif command == "add":
        set_name = command_list[1]
        path = command_list[2]
        set_add_path(set_name, path)
    elif command == "delete":
        option = command_list[1]
        delete_set(option)
    elif command == "list":
        list_sets()

#--------------------------------------------------------

def main():
    data = load_data()
    current_set = data["current_set"]
    header(app_title)
    #print("[>] Current set: " + current_set)
    print("(type \"help\" for more information)")
    print("\n\n")
    while True:

        select = input("[~] ").split()
        cursor = select[0]
        commands = select[1:]

        if cursor == "help":
            help_handler()
        elif cursor in quit_terms:
            sys.exit()
        elif cursor == "set":
            manage_sets(commands)
        elif cursor == "clear":
            clear()
            header(app_title)
        else:
            print(f"\n[>] Not a recognized option: \"{cursor}\". Enter \"help\" for more infomration.")

#---------------------------------------------------------
# Evaluate CLI arguments  

if cli_args:
    if cli_args[0] == "-a" or cli_args[0] == "--add":
        add_directory(os.getcwd())
        sys.exit()


clear()
main()
        
