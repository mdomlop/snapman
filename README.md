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

For futher details, read the included documentation:

- [Snapman manual](man/en/snapman.1.md), for the manual.

- [Configuration manual](man/en/snapman.5.md), for the manual of configuration
    file syntax.

When the program is installed, all the documentation are available at
`/usr/share/doc/snapman`. And the manuals with:

        man snapman

And, for configuration file syntax:

        man 5 snapman
Installation
------------

You can choose between different installation methods.

### Classic method ###

- Build and install:

        $ make
        # make install

- Uninstall:

        # make uninstall


### Arch Linux package ###

- Build and install:

        $ make pkg
        # pacman -U snapman-*.pkg.xz

- Uninstall:

        # pacman -Rsc snapman


### Debian package ###

- Build and install:

        $ make deb
        # dpkg -i snapman_*.deb

- Uninstall:

        # apt purge snapman
Usage
-----

First of all edit the configuration file at `/etc/snapman.ini`. A default one is
supplied as example. Alternatively you use the `--sample` command line option to
generate one:

        # snapman --sample > /etc/snapman.ini

Then edit `/etc/snapman.ini` at your preferences. You can edit `[DEFAULT]`
section, but not change the name _DEFAULT_. It is essential to the right working
of the program, due to the other sections inherit properties from it.

You can read `man 5 snapman` to a complete reference of configuration file
format.

We'll go to show a little example. In it we make snapshots for the root
filesystem and the `/home` directory.

        $ cat /etc/snapman.ini
        [DEFAULT]
        subvolume = /
        frequency = 1d
        quota = 30
        readonly = True
        enabled = True

        [/snapshots]

        [/home/snapshots]
        subvolume = /home

Now execute as root:

        # snapman

The program will create two snapshots. One for each section at directory
especified by subvolume option:

        $ ls /snapshots /home/snapshots
        /snapshots:
        20171025-084416

        /home/snapshots:
        20171025-084416

In the case of `[/snapshots]` section the subvolume option was inherit from
`[DEFAULT]` section.

If we execute again `snapman` no action will be runned, due to the frequency
option is `1d` (one day). Only when the difference is greater than one day
would make a new snapshot.

When the number of snapshots is greater than the specified by `quota` option
the older snapshot will be deleted and a new one will be created.

The `readonly` option makes readonly snapshots and the `enabled` option allows
to disable this section, without delete snapshots. Both options accept boolean
values: True, False, 0, 1, on, off.

Rather than executing manually every certain time, we can use the `--daemon`
command line option:

        # snapman --daemon

And then the program will make copies when necessary to meet the indicated
frequency.

For that, a systemd service is included. Just start and enable it:

        # systemctl start snapman
        # systemctl enable snapman

Or, if you do no use systemd, add a line like `snapman --daemon` to your
`/etc/rc.local` or whatever it is that uses your startup system.


### Command line options.

Snapman program allows to manage snapshots by command line. Here some examples.

To show all command line options:

        $ snapman --help

A list of managed sections:

        $ snapman --sections

A list of snapshots of a section:

        $ snapman --section-snapshots /home/snapshots

Show information of a section:

        $ snapman --section-info /home/snapshots

Delete all snapshots of a section:

        # snapman --section-clean /home/snapshots

To show additional information when performing actions use `--verbose` option.

There are more command line options. Please refer to `man snapman` to complete
and updated guide.
