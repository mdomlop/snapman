Snapman
-------

Snapman is a backup program based on the ability of Btrfs file system to
capture snapshots of subvolumes.

When you run `snapman` it will read its configuration file and then it will
make backups (snapshots) of indicated subvolumes at desired frequency until
reach a defined quota. If quota were reached, then it will remove the older
backup before to make a new one to keep the number of backups indicated in
quota.

Snapman will run periodically if you use the `--daemon` command line option.

Backups are stored in a directory specified in the configuration file.

For each subvolume that you want to backup you must to write at least an entry
in the configuration file (in the easy `.ini` format).

Snapman accepts command-line options to manage snapshots.

For futher details about the configuration, installation or other features you
can read the included manual.

