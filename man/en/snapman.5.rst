=============
 snapman.ini
=============

--------------------------------------
Configuration file of ``snapman``
--------------------------------------

:Author: Manuel Domínguez López <mdomlop@gmail.com>
:Date:   2018-08-25
:Copyright: GPLv3
:Version: 1.0a
:Manual section: 5
:Manual group: configuration files


LOCATION
========

``/etc/snapman.ini``

DESCRIPTION
===========

``snapman`` is a backup program based on the ability of Btrfs file
system to capture snapshots of subvolumes.

When you run ``snapman`` without options it will read the default
configuration file in ``/etc/snapman.ini`` and then it will make backups
(snapshots) of indicated subvolumes at desired frequency until reach a
defined quota. I quota were reached, then it will remove the older
backup before to make a new one to keep the number of backups indicated
in quota.

The configuration file defines all the stuff about what and how the
snapshots of subvolumes are taked. Read more about it in snapman(5).

The configuration file is mandatory. If there is not such file, the
program will fail. You can indicate an altenative configuration file
with the ``--config`` option.

You can print to ``stdout`` an example configuration file with the
``--config-sample`` option.

FORMAT
======

The configuration file was writed in ``.ini`` format that was
interpreted by ``parseconfig`` module of ``python3``.

This file was divided in sections. Sections names are lines in square
brackets. Each section name represents a way to make snapshots. To
define this each section can content some properties.

AVAILABLE PROPERTIES
====================

Properties are ``key = value`` formated lines besides the section name.
As in the example:

::

       [Section Name 1]
       Property1 = value
       Property2 = value
       ...

       [Section Name2]
       Property1 = value
       ...

Each section stores the configuration for a subvolume’s snapshots. The
properties set how the snapshots will be taked.

May be differents configuration sections for the same subvolume (with
the same subvolume property).

**[Section Name]** The section name must be unique. It encodes the full
path to directory in wich the copies will be stored. No ending ‘/’ in
such path are allowed.

There is a section named as ``[DEFAULT]`` of which all its properties
are inherited by the others if there are omited. Such section will no
generate any snapshot by itself, it only serves as a method to take
default values for other sections.

**subvolume**
   Full path to subvolume to copy. Without ending ‘/’.
**frequency**
   The frequency with which the copies will be made. This can be
   expresed in seconds: 1234 or 123s, minutes: 5m, hours: 1h, days: 7d,
   or even years: 1y. But not a combination of any of them: 1h15m. For
   example, in cases like that, please simplify in minutes: 75m.
**quota**
   It is the number of snapshots that you want to keep in the directory.
**readonly**
   Set in ``True`` for a readonly snapshot, ``False`` for a writable
   one.
**enabled**
   Set in ``True`` for enable snapshotting, ``False`` for disabling.
**timestamp**
   Set the timestamp format. See
   https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior.
**umask**
   Set the umask value for the creation of the directory in where copies
   will be stored.

EXAMPLES
========

::

       [DEFAULT]
       subvolume = /
       frequency = 1d
       quota = 30
       readonly = True
       enabled = True
       timestamp = %Y%m%d-%H%M%S
       umask = 022

       [/backups/OS]
       
       [/data/snapman/movies]
       subvolume = /data/movies
       frequency = 7d
       quota = 10
       readonly = False

       [/data/snapman/music]
       subvolume = /data/music
       quota = 10

       [/data/snapman/documents/daily]
       subvolume = /data/documents
       frequency = 1h
       quota = 24

       [/data/snapman/documents/last20min]
       subvolume = /data/documents
       frequency = 5m
       quota = 4
      
       [/data/snapman/documents/5min]
       subvolume = /data/documents
       frequency = 1m
       quota = 5
       enabled = False
      

BUGS
====

Probably. If you found any let me know, please.


SEE ALSO
========

snapman(1)
