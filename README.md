# PackRat

## Overview
PackRat is an archive utility using Python. It uses tar/gzip to create archives based
on settings the user defines. The user defines "packs", or named lists of directories, that have
their own individual settings and statistics. 

### Features
- Paths can be added to a set directly from the command line, with the `packrat -a {set}` command.

### Example
1. Create the "music" set.
<br>
`set create music`
1. Add the directory to the set.
<br>
`set add music ~/Music`
1. Define the archive file path. The "%" character tells PackRat to add today's date.
<br>
`set target music /mnt/Backups/music_%.tar.gz`
1. Run the tar command.
<br>
`set run music`



