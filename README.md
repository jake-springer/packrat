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

# To Do

- [ ] run > check that there's a tarpath, and other paths saved
- [ ] check if a path is included in multiple sets
- [ ] ascii header pls
- [ ] cool visual stuff like changing the font color
- [ ] Functionality for the ~/ path
- [ ] add records functionality 
- [ ] "not enough options for "random command that doesn't exists""
- [ ] default directory for tar.gz files
- [ ] check for write perms in directories
 
### 0.1
- [X] add directories in cli interface
- [X] Do the same five lines of code every time a set is modified. 
- [X] "list" cli arg
- [X] create set "main" when init new data.json
- [X] set info -> show detailed info about a set
- [X] Need error handling for when not enough options are passed
- [X] Actual help manager
- [X] set marker in tarfile to add date in file name
- [X] Archive records, last time set was archived. 
 
### 0.2
- [X] display version id
 

## Errors

101 -> 	add_directory() 	->	failed to add path to the json file failed os.path.exists()

102 -> 	pull_set() 			-> 	failed to load set from json with the given set_name value 

103 ->  save_set() 			-> 	failed to find set name in json. likely the set['name'] value was modified 

104 -> 	cli_handler() 		-> 	set_name wasn't provided in the cli arguments.

105 ->  manage_sets()		->  not enough options provided for the given command.

106 ->  help_handler()      ->  no value for the provided key in help_info

107 ->	add_set()			->  tried to create a set with an existing name

108 ->  set_drop_dir()		->  tried to set a path that doesn't exist, failed os.path.exists()


