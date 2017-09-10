% SNAPMAN(5)
% Manuel Domínguez López
% July 2017

# NAME

snapman.ini - Configuration file of `snapman`

# LOCATION

`/etc/snapman.ini`

# DESCRIPTION

`snapman` is a backup program based on the ability of Btrfs file system to 
capture snapshots of subvolumes.

When you run `snapman` without options it will read the default 
configuration file in `/etc/snapman.ini` and then it will make 
backups (snapshots) of indicated subvolumes at desired frequency until
reach a defined quota. I quota were reached, then it will remove the older
backup before to make a new one to keep the number of backups indicated in
quota.

The configuration file defines all the stuff about what and how the 
snapshots of subvolumes are taked. Read more about it in snapman(5).

The configuration file is mandatory. If there is not such file, the 
program will fail. You can indicate an altenative configuration file
with the `--config` option.

You can print to `stdout` an example configuration file with the 
`--sample` option.

# FORMAT

The configuration file was writed in `.ini` format that was interpreted by `parseconfig` module of `python3`.

This file was divided in sections. Sections names are lines in square brackets. Each section name represents a way to make snapshots. To define this each section can content some properties.

# AVAILABLE PROPERTIES

Properties are `key = value` formated lines besides the section name. As in the example:

        [Section Name 1]
        Property1 = value
        Property2 = value
        ...

        [Section Name2]
        Property1 = value
        ...

There is a section named as `[DEFAULT]` of which all its properties are inherited by the others if there are omited. Such section will no generate any snapshot by itself, It only serves as a method to
take default values for other sections.

**store**
:    The directory where were stored the snapshots.

**subvolume**
:    Full path to subvolume to copy.

**directories**
:    Directories are in *name*:*frequency*:*quota* format. Which there is three fields separated by a colon.

    - First field is the name of the directory.

    - Second one is the frequency with which the copies will be made. This can be expresed in seconds: 1234 or 123s, minutes: 5m,
hours: 1h, days: 7d, or even years: 1y. But not a combination of any of them.

    - The third field is the quota. It is the number of snapshots that you want to keep in the directory.

**readonly**
:    True for a readonly snapshot.

# BUGS

Probably. If you found any let me know, please.

# COPYRIGHT

GPLv3

# SEE ALSO

snapman(1)


