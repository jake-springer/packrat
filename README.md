# PackRat

## Overview
PackRat is an archive utility using Python. It uses tar/gzip to create archives based
on settings the user defines. The user defines "packs", or named lists of directories, that have
their own individual settings and statistics. 

### Features
- Paths can be added to a set directly from the command line, with the `packrat -a {set}` command.

### Example
1. Create the "music" set.
`set create music`
1. Add the directory to the set.
`set add music ~/Music`
1. Define the archive file path. The "%" character tells PackRat to add today's date.
`set target music /mnt/Backups/music_%.tar.gz`
1. Run the tar command.
`set run music`

# To-Do

- [ ] check if a path is included in multiple sets
- [ ] cool visual stuff like changing the font color
- [ ] "not enough options for "random command that doesn't exists""
- [ ] default directory for tar.gz files
- [ ] check for write perms in directories
- [ ] make sure a path isn't being added to the same set more than once

 
- [X] add directories in cli interface
- [X] Do the same five lines of code every time a set is modified. 
- [X] "list" cli arg
- [X] create set "main" when init new data.json
- [X] set info -> show detailed info about a set
- [X] Need error handling for when not enough options are passed
- [X] Actual help manager
- [X] set marker in tarfile to add date in file name
- [X] Archive records, last time set was archived. 
- [X] run() -> check that there's a tarpath, and other paths saved
- [X] ascii header pls
- [X] Functionality for the ~/ path
- [X] add records functionality 
- [X] display version id
 

# Errors

101 -> 	add_directory() 	->	failed to add path to the json file failed os.path.exists()

102 -> 	pull_set() 			-> 	failed to load set from json with the given set_name value 

103 ->  save_set() 			-> 	failed to find set name in json. likely the set['name'] value was modified 

104 -> 	cli_handler() 		-> 	set_name wasn't provided in the cli arguments.

105 ->  manage_sets()		->  not enough options provided for the given command.

106 ->  help_handler()      ->  no value for the provided key in help_info

107 ->	add_set()			->  tried to create a set with an existing name

108 ->  set_drop_dir()		->  tried to set a path that doesn't exist, failed os.path.exists()
109 ->  default_target()    ->  tried to create a default tarfile path, but no dropdir configured.


# Change Log

## 0.2.1
- create_set() 		-> checks if set with matching name exists, cancels saving if true.
- set_info()   		-> displays a value based on the sets last_ran attribute
- set_drop_dir() 	-> changes the drop_dir value in the settings 
