#!/usr/bin/env python3

PROGRAM_NAME = 'snapman'
DESCRIPTION = 'Create and manage filesystem snapshots'
VERSION='0.9.1b'
AUTHOR = 'Manuel Domínguez López'  # See AUTHORS file
MAIL = 'mdomlop@gmail.com'
LICENSE = 'GPLv3+'  # Read LICENSE file.


import os
import time
import datetime
import sys  # only for sys.stderr
import subprocess
from subprocess import DEVNULL
import configparser  # for parse config file
import argparse
import threading

class Section():
    ''' The Section class represents a individual section in config file. '''
    def __init__(self, name):
        if name in settings.sections():
            self.subvolume = settings[name]['subvolume']
            self.frequency = settings[name]['frequency']
            self.frequency_sec = toseconds(self.frequency)
            self.quota = settings[name].getint('quota')
            self.readonly = settings[name].getboolean('readonly')
            self.enabled = settings[name].getboolean('enabled')
            self.sformat = settings[name]['timestamp']
        else:
            clean_exit('Section not found: ' + name, 8)

        self.name = name  # The name of section in config file (a path).

    def snapshot_list(self, path=True):
        ''' Return a list of snapshots or a empty list '''
        try:
            l = os.listdir(self.name)
        except FileNotFoundError:
            l = []
        if path:
            l = list(map(lambda x: os.path.join(self.name, x), l))
        return(l)

    def print_snapshots(self, path=True):
        for i in self.snapshot_list():
            print(i)

    def print_properties(self, title=False, explicity=False):
        props = ('subvolume', 'frequency', 'quota', 'readonly', 'enabled')
        if title:
            print('[' + self.name + ']')
        for i in props:
            if explicity:
                if settings['DEFAULT'][i] != settings[self.name][i]:
                    print(i, '=', settings[self.name][i])
            else:
                print(i, '=', settings[self.name][i])

    def percent(self):
        return(round(int(self.snapshot_count()) * 100 / self.quota))

    def info(self):
        if args.verbose:
            print('Section:', self.name)
        print(
            'From:', self.subvolume +
            '\nSnapshots:', str(self.snapshot_count()) + '/' + str(self.quota) +
            '\nQuota:', str(self.percent()) + '%' +
            '\nNewer:', self.newer_snapshot() +
            '\nOlder:', self.older_snapshot() +
            '\nEnabled:', self.enabled
            )

    def snapshot_count(self):
        return(len(self.snapshot_list()))

    def newer_snapshot(self, fullpath=True):
        if self.snapshot_count():
            return(self.snapshot_list(fullpath)[-1])
        else:
            return('')

    def older_snapshot(self, fullpath=True):
        if self.snapshot_count():
            return(self.snapshot_list(fullpath)[0])
        else:
            return('')

    def quota_diff(self):
        return(self.snapshot_count() - self.quota)

    def now(self):
        return(datetime.datetime.now().strftime(self.sformat))

    def ts(self, t):
        try:
            d = datetime.datetime.strptime(t, self.sformat)
        except ValueError:
            clean_exit('ERROR: Bad format found in ' +
                       os.path.join(self.name, t), 9)
        return(time.mktime(d.timetuple()))

    def write(self):
        dest = os.path.join(self.name, self.now())
        if self.readonly:
            cmd = ('btrfs', 'subvolume', 'snapshot', '-r',
                   self.subvolume, dest)
        else:
            cmd = ('btrfs', 'subvolume', 'snapshot', self.subvolume, dest)
        if args.verbose:
            subprocess.call(cmd)
        else:
            subprocess.call(cmd, stdout=DEVNULL)

    def delete(self, dest):
        cmd = ('btrfs', 'subvolume', 'delete', dest)
        if args.verbose:
            subprocess.call(cmd)
        else:
            subprocess.call(cmd, stdout=DEVNULL)

    def snapshot_clean(self):
        for i in self.snapshot_list():
            s = os.path.join(self.name, i)
            self.delete(s)
        if os.path.isdir(self.name):
            self.delete(self.name)

    def clean_quota(self):
        quota_diff = self.quota_diff()
        if quota_diff > 0:
            for i in range(quota_diff):  # 0..quota_diff - 1
                self.delete(self.older_snapshot())

    def makesnapshot(self):
        # Only do actions if enabled property is on:
        if not self.enabled:
            if args.verbose:
                print('WARNING: Section', self.name, 'is disabled',
                      file=sys.stderr)
            return(0)
        try:
            if not os.path.isdir(self.name):
                dirname = os.path.dirname(self.name)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname, exist_ok=True)
                cmd = ('btrfs', 'subvolume', 'create', self.name)
                subprocess.call(cmd, stdout=DEVNULL)
        except PermissionError:
            clean_exit('ERROR: I can not create the directory: ' +
                       self.name, 5)
        self.clean_quota()
        if self.snapshot_count() == 0:  # Make a copy if directory is empty.
            self.write()
        else:
            # Make a copy if newer copy is older than minage.
            diff = self.ts(self.now()) - self.ts(self.newer_snapshot(False))
            if diff > self.frequency_sec:
                if self.quota_diff() == 0:  # Make room for a new snapshot.
                    self.delete(self.older_snapshot())
                self.write()

    def start(self):
        while True:
            self.makesnapshot()
            time.sleep(self.frequency_sec)

    def daemonize(self):
        threading.Thread(target=self.start).start()


def toseconds(period):
    '''Read minutes, hours, days or years and converts it to seconds.'''
    period = str(period)
    if period.endswith('s'):
        fperiod = period.replace('s', '')
    elif period.endswith('m'):
        fperiod = period.replace('m', '')
    elif period.endswith('h'):
        fperiod = period.replace('h', '')
    elif period.endswith('d'):
        fperiod = period.replace('d', '')
    elif period.endswith('y'):
        fperiod = period.replace('y', '')
    else:
        fperiod = period
    try:
        int(fperiod)
    except:
        clean_exit(
            'ERROR:I do not know how to convert ' + period + ' to seconds', 2)
    fperiod = int(fperiod)
    if period.endswith('m'):
        fperiod = fperiod * 60
    elif period.endswith('h'):
        fperiod = fperiod * 60 * 60
    elif period.endswith('d'):
        fperiod = fperiod * 60 * 60 * 24
    elif period.endswith('y'):
        fperiod = fperiod * 60 * 60 * 24 * 365

    return(fperiod)


def parseargs():
    # Default options:
    configfile = '/etc/snapman.ini'  # Configuration file
    pidfile = None  # Writes pidfile.

    parser = argparse.ArgumentParser(
            prog=PROGRAM_NAME,
            description=DESCRIPTION
            )

    parser.add_argument('-c', '--configfile', default=configfile,
                        help='Alternative configuration file')
    parser.add_argument('-p', '--pidfile', default=pidfile,
                        help='Write a pidfile')
    parser.add_argument('-s', '--sample', default=False, action='store_true',
                        help='Print out a sample configuration file')
    parser.add_argument('-d', '--daemon', default=False, action='store_true',
                        help='Execute in daemon mode')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Set verbosity on if available')
    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + VERSION,
                        help='Show program version and exit')

    parser.add_argument('--sections', default=False, action='store_true',
                        help='List managed sections')
    parser.add_argument('--section-snapshots', default=None,
                        help='List of snapshots taked from the section')
    parser.add_argument('--section-clean', default=None,
                        help='Delete all snapshots taked from the section')
    parser.add_argument('--section-info', default=None,
                        help='Show some information about the section status')
    parser.add_argument('--section-properties', default=None,
                        help='Print the properties configured for the section')

    parser.add_argument('--subvolumes', default=False, action='store_true',
                        help='List subvolumes managed by configuration file')
    parser.add_argument('--subvolume-snapshots', default=None,
                        help='List snapshots taked from the given subvolume')
    parser.add_argument('--subvolume-sections', default=None,
                        help='List sections which manage the given subvolume')
    parser.add_argument('--subvolume-clean', default=None,
                        help='Delete all snapshots taked from given subvolume')
    parser.add_argument('--subvolume-info', default=None,
                        help='Show information about the subvolume status')

    parser.add_argument('--snapshots', default=False, action='store_true',
                        help='Show a list of all subvolumes taked')
    parser.add_argument('--snapshot-info', default=None,
                        help='Show information about the snapshot status')

    if not os.path.exists(parser.parse_args().configfile):
        clean_exit('ERROR: I can not find the configuration file.', 1)

    return(parser.parse_args())


def get_settings():
    ''' Get settings from config file. Overwrited by command line options. '''
    settings = configparser.ConfigParser()
    settings.read(args.configfile)

    # Exit if there are troubles with the configuration file:
    try:
        f = open(args.configfile, "r")
    except IsADirectoryError:
        clean_exit('ERROR: \'' + args.configfile + '\' is a directory.', 7)
    except FileNotFoundError:
        clean_exit('ERROR: \'' + args.configfile + '\' does not exists.', 7)
    except IOError:
        clean_exit(
                'ERROR: I/O error loading config file: \'' +
                args.configfile, 7
                )
    except:
        clean_exit(
                'ERROR: Unknown error while loading config file: \'' +
                args.configfile, 7
                )
    else:
        f.close()

    return(settings)


def clean_exit(text=None, exitnum=0):
    if text:
        print(text, file=sys.stderr)
    try:
        os.remove(pidpath)
    except NameError:
        sys.exit(exitnum)
    sys.exit(exitnum)


def daemon():
    for i in settings.sections():
        x = Section(i)
        x.daemonize()


def run_once():
    for i in settings.sections():
        x = Section(i)
        x.makesnapshot()


def main():
    global settings
    global args

    args = parseargs()
    settings = get_settings()

    if args.pidfile:
        PID = os.getpid()
        pidfile = open(args.pidfile, 'w')
        pidfile.write(str(PID))
        pidfile.close()

    if args.sample:
        print('''\
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
''')

    elif args.sections:
        if not args.verbose:
            for i in settings.sections():
                print(i)
        else:
            for i in settings.sections():
                x = Section(i)
                r = 'readonly' if x.readonly else 'writable'
                print(x.name + ':',
                      str(x.snapshot_count()) + '/' + str(x.quota),
                      r, 'from', x.subvolume)
    elif args.section_snapshots:
        s = args.section_snapshots.rstrip('/')
        x = Section(s)
        if args.verbose:
            l = x.snapshot_list()
            for i in l:
                print(i, 'from', x.subvolume)
        else:
            x.print_snapshots()
    elif args.section_clean:
        s = args.section_clean.rstrip('/')
        x = Section(s)
        x.snapshot_clean()
    elif args.section_info:
        s = args.section_info.rstrip('/')
        x = Section(s)
        x.info()
    elif args.section_properties:
        s = args.section_properties.rstrip('/')
        x = Section(s)
        if args.verbose:
            x.print_properties(True)
        else:
            x.print_properties()

    elif args.subvolumes:
        l = []
        for s in settings.sections():
            l.append(settings[s]['subvolume'])
        for i in sorted(set(l)):
            print(i)
    elif args.subvolume_snapshots:
        sub = args.subvolume_snapshots
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        for i in settings.sections():
            if sub == settings[i]['subvolume']:
                found = True
                x = Section(i)
                if not args.verbose:
                    x.print_snapshots()
                else:
                    for s in x.snapshot_list():
                        print(s, 'from', x.subvolume)
        if not found:
            clean_exit('No section manages the subvolume: ' + sub, 6)
    elif args.subvolume_sections:
        sub = args.subvolume_sections
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        for i in settings.sections():
            if sub == settings[i]['subvolume']:
                found = True
                x = Section(i)
                if not args.verbose:
                    print(x.name)
                else:
                    print(x.name + ':', x.snapshot_count())
        if not found:
            clean_exit('No section manages the subvolume: ' + sub, 6)

    elif args.subvolume_clean:
        sub = args.subvolume_clean
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        for i in settings.sections():
            if sub == settings[i]['subvolume']:
                found = True
                x = Section(i)
                x.snapshot_clean()
        if not found:
            clean_exit('No section manages the subvolume: ' + sub, 6)

    elif args.subvolume_info:
        sub = args.subvolume_info
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        snap = []
        sect = []
        for i in settings.sections():
            if sub == settings[i]['subvolume']:
                found = True
                x = Section(i)
                snap += x.snapshot_list()
                sect.append(x.name)

        if not found:
            clean_exit('No section manages the subvolume: ' + sub, 6)
        if snap:
            sort_snaps = sorted(snap)
            newer = sort_snaps[0]
            older = sort_snaps[-1]
        else:
            newer = ''
            older = ''
        if args.verbose:
            print('Subvolume:', sub)
        print('Snapshots:', len(snap),
              '\nSections:', len(sect),
              '\nNewer:', newer,
              '\nOlder:', older)

    elif args.snapshots:
        for s in settings.sections():
            x = Section(s)
            if args.verbose:
                l = x.snapshot_list()
                for i in l:
                    print(i, 'from', x.subvolume)
            else:
                x.print_snapshots()
    elif args.snapshot_info:
        snap = args.snapshot_info
        if snap != '/':  # Prevent strip filesystem root.
            snap = snap.rstrip('/')
        else:
            clean_exit("Root directory can't be a snapshot!", 4)
        found = False
        for i in settings.sections():
                x = Section(i)
                if snap in x.snapshot_list():
                    found = True
                    print('Section:', x.name,
                          '\nSubvolume:', x.subvolume)
        if not found:
            clean_exit('No section manages the subvolume: ' + snap, 6)

    elif args.daemon:
        daemon()
    else:
        run_once()


if __name__ == '__main__':
    main()
    clean_exit()
