import sys
import gettext

EXECUTABLE_NAME = 'snapman'

gettext.translation(EXECUTABLE_NAME, localedir="/usr/share/locale",
                    fallback=True).install()


PROGRAM_NAME = 'Snapman'
DESCRIPTION = 'Create and manage filesystem snapshots'
VERSION = '1.1a'
AUTHOR = 'Manuel Domínguez López'  # See AUTHORS file
MAIL = 'mdomlop@gmail.com'
SOURCE = "https://github.com/mdomlop/snapman"
LICENSE = 'GPLv3+'  # Read LICENSE file.

PYVER = ".".join((
    str(sys.version_info[0]),
    str(sys.version_info[1]),
    str(sys.version_info[2])))

COPYRIGHT = '''
Copyright: 2018 Manuel Domínguez López <mdomlop@gmail.com>
License: GPL-3.0+

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This package is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 .
 On Debian systems, the complete text of the GNU General
 Public License version 3 can be found in "/usr/share/common-licenses/GPL-3".
'''

SAMPLE ='''
# This is the config file for snapman.py. It will be parsed by configparser
# python module.
# Copy this file in /etc/snapman.ini and edit it at your preferences.

# The section name is the absolute path to directory where the snapshots
# were be stored.
# [DEFAULT] section is special. The rest of sections take their values from it
# by default.

[DEFAULT]
# Default values for all sections.
# Full path to subvolume to copy:
subvolume = /
# The frequency in seconds, minutes, hours, days or years (see man 5 snapman):
frequency = 1d
# The maximun number of allowed snapshots:
quota = 30
# Set to True for a readonly snapshot, otherwise set to False:
readonly = True
# Set to True for enable snapshotting, otherwise set to False:
enabled = True
# Set the timestamp format.
# See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
timestamp = %Y%m%d-%H%M%S

[/.snapshots]
# Snapshots of root directory at /.snapshots with default frequency and quota.

[/home/user/.snapshots]
# Writables snapshots of a user home directory every hour of the last 24 hours.
subvolume = /home/user
frequency = 1h
quota = 24
readonly = False

[/home/user/Recent]
# Writables snapshots of a user home directory every 5 minutes. Until the
# last half hour.
# Useful, among other things, to cheat the mincraft game. To do this
while gaming if you die:
# 1. Save and Quit to Title
# 2. Open a terminal and write:
# rsync -aHv --delete ~/Recent/backup of 5m ago/.minecraft/ ~/.minecraft/
# 3. Return to the game and enjoy your inmortality. ;-)
subvolume = /home/user
frequency = 5m
quota = 6
readonly = False

[/pools/DATA/Copies/Music]
# Default values to snapshots of /pools/DATA/Music at /pools/DATA/Copies/Music
'''
