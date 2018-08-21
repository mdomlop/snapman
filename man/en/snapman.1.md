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
reach a defined quota. If quota were reached, then it will remove the older
backup before to make a new one to keep the number of backups indicated in
quota.

The configuration file defines all the stuff about what and how the
snapshots of subvolumes are taked. Read more about it in snapman(5).

The configuration file is mandatory. If there is not such file, the
program will fail. You can indicate an altenative configuration file
with the `--config` option.

You can print to `stdout` an example configuration file with the
`--sample` option.

# GUI MODE EXECUTION

If you use the `--gui` option, program will show a Qt5 interface.

# DAEMON MODE EXECUTION

You can run periodically this program if you use the `--daemon` option.

Because a misconfigured or non-existent configuration file does not allow the
execution of the program, such file only is readed one time. I you performs
changes on it, you may to restart the program, if you want these changes to be
applied.

# SYSTEMD SERVICE

A systemd service was provided for execute in daemon mode. Just start and
enable `snapman.service`.

As mentioned before, you must restart the service if you performs changes on
configuration file and want these changes to be applied.

# OPTIONS

## General options

**-c**, **--configfile**=[*file*]
:    Use an alternative configuration file *file* rather than the default one
`/etc/snapman.ini`.

**-d**, **--daemon**
:    Start the program in daemon mode. In this mode `snapman` will keep in
execution performing snapshots when necessary.

**-h**, **--help**=[*file*]
:    Show help message and exit.

**-s**, **--sample**
:    Print a sample configuration file to stdout and exit.

**-v**, **--verbose**
:    Set verbosity on. This option shows additional information in the command
output, if available for such command.

**--pidfile**=[*file*]
:    Write the PID of the program to *file*. *file* must be a full path.
Usually `/run/snapman.pid`.

**--version**
:    Show program version and exit.


## Section related options

**--sections**
:   Print a list of all sections currently managed by the program.

**--section-snapshots**=[*section*]
:   Print a list of all snapshots taked by the section *section*.

**--section-clean**=[*section*]
:   Delete all snapshots taked by the section *section*.

**--section-info**=[*section*]
:   Print out some information about the section *section*.

**--section-properties**=[*section*]
:   Print out the properties of the section *section*.

**--section-newsnapshot**=[*section*]
:   Force creation of a new snapshot.

## Subvolume related options

**--subvolumes**
:   Print a list of all subvolumes currently managed by the program.

**--subvolume-snapshots**=[*/path/to/subvolume*]
:   Print a list of all snapshots taked from subvolume */path/to/subvolume*.

**--subvolume-sections**=[*/path/to/subvolume*]
:   Prints a list of all the sections that manage the given subvolume
*/path/to/subvolume*.

**--subvolume-clean**=[*/path/to/subvolume*]
:   Delete all snapshots taked from subvolume */path/to/subvolume*.

**--subvolume-info**=[*/path/to/subvolume*]
:   Print out some information about the subvolume */path/to/subvolume*.

## Snapshot related options

**--snapshots**
:   Print a list of all snapshots currently managed by the program.

**--snapshot-info**=[*/path/to/snapshot*]
:   Print out some information about the snapshot */path/to/snapshot*.

# RETURN VALUES

**0**
:    Normal exit. No errors founded.

**1**
:    Configuration file not found, or incorrect.

**2**
:    Section not found.

**3**
:    Snapshot not found.

**4**
:    Subvolume not found.

**5**
:    Frequency conversion error.

**6**
:    Incorrect timestamp format.

**7**
:    Directory creation error.

**8**
:    Failed to create, or delete the pidfile.

**130**
:    `KeyboardInterrupt` signal received.

# FILES

**`/etc/snapman.ini`**
:    Default configuration file provided. Sets all stuff about snapshots. Edit
at your preferences. See snapman(5).

**`/lib/systemd/system/snapman.service`**
:    The systemd service.


# HISTORY

The idea arose inspired by the program Time Machine® own of the system Mac OS
X. However, they do not have the slightest similarity. Originally this program
was called Timemachine. But because 'Time Machine' is a trademark of Apple® I
decided to change its name to Snapman.

# BUGS

Probably. If you found any let me know, please.


# COPYRIGHT

GPLv3


# SEE ALSO

snapman(5)

