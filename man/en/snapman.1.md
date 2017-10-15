% SNAPMAN(1)
% Manuel Domínguez López
% October 2017

# NAME

snapman - A Btrfs based backup program

# SYNOPSIS

`snapman` [*OPTION*...]

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

# DAEMON MODE EXECUTION

You can run periodically this program if you use the `--daemon` option.

Because a misconfigured or non-existent configuration file does not allow the execution of the program, such file only is readed one time. I you performs changes on it, you may to restart the program, if you want these changes to be applied.

# SYSTEMD SERVICE

A systemd service was provided for execute in daemon mode. Just start and enable `snapman.service`.

As mentioned before, you must restart the service if you performs changes on configuration file and want these changes to be applied.

# OPTIONS

**-c**, **--configfile**=[*file*]:
:    Uses an alternative configuration file *file* rather than the default one `/etc/snapman.ini`.

**-s**, **--sample**
:    Prints a sample configuration file to stdout and exits.

**-h**, **--help**
:    Prints information about usage and exits.

**-d**, **--daemon**
:    Starts the program in daemon mode. In this mode `snapman` will keep in execution performing snapshots when necessary.
    
**--pidfile**=[*file*]:
:    Writes the PID of the program to *file*.

**--section-list**
:   Prints a list of all sections managed from configuration file.

**--section-snapshot-list** *Section name*
:   Prints a list of all snapshots taked by the section *Section name*.

**--section-snapshot-clean** *Section name*
:   Deletes all snapshots taked by the section *Section name*.

**--section-info** *Section name*
:   Prints out some information of the section *Section name*.

**--section-properties** *Section name*
:   Prints out the properties of the section *Section name*.

**--subvolume-list**
:   Prints a list of all subvolumes managed from configuration file.

**--subvolume-snapshot-list** */path/to/snapshot*
:   Prints a list of all snapshots taked from subvolume */path/to/subvolume*.

**--subvolume-snapshot-clean** */path/to/snapshot*
:   Deletes all snapshots taked from subvolume */path/to/subvolume*.

**--subvolume-info** */path/to/subvolume*
:   Prints out some information of the subvolume */path/to/subvolume*.

**--snapshot-info** */path/to/snapshot*
:   Prints out some information of the snapshot */path/to/snapshot*.

# RETURN VALUES

**0**
:    Normal exit. No errors founded.

**1**
:    The program can not found the configuration file.
    
**2**
:    Failed to convert to seconds the frecuency value from configuration file.
    
**3**
:    Snapshots stored in disk have a name in a format that not match with `%Y-%m-%d %H:%M:%S` format.

**130**
:    `KeyboardInterrupt` signal received.
    
# FILES

**`/etc/snapman.ini`**
:    Default configuration file provided. Sets all stuff about snapshots. Edit at your preferences. See snapman(5).
    
**`/usr/lib/systemd/system/snapman.service`**
:    The systemd service.


# HISTORY

The idea arose inspired by the program Time Machine® own of the system Mac OS X. However, they do not have the slightest similarity. Originally this program was called Timemachine. But because 'Time Machine' is a trademark of Apple® I decided to change its name to Snapman.

# BUGS

Probably. If you found any let me know, please.


# COPYRIGHT

GPLv3


# SEE ALSO

snapman(5)

