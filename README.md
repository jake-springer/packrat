# PackRat V2

## Overview
**Reworked 5/16/24**
Backup utility for Linux systems, written in Python. 
PackRat is used to flag directories that require regular backups, and automates the process when needed.
It creates tar/gzip archives and stores them in the specified directory. 

## Setup
The `app_packrat.py` script is the TUI, front-end portion, which imports `packrat.py` for all of the actual work. I put them both in `/usr/local/bin` and alias `app_packrat.py` as `rat` or something. 

## Usage 
- On initial startup, packrat creates the default config file in the users home directory.
- Use `packrat --help` for information on all options
- `packrat --list`: show all flagged directories
- `packrat --del`: remove a directory from the flagged list
- `packrat --add {path}`: flag a directory for backup

- `packrat pack {all/ID/here}`
  - `all`: go through each flagged directory and create a backup
  - `ID`: use the number given to a directory as shown with the `packrat --list` command, backup that single directory
  - `here`: backup the current directory. This does *not* flag the directory for future backups. 

## To-Do
- [ ] Reimplement the `change_backups_dir()` function from v1
- [ ] Check permissions of the backups directory
- [ ] Error code system for better debugging
- [ ] systemd timer script for automation 
