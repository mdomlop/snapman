#!/usr/bin/env python3

"""
Snapman
=======

Create snapshots using BTRFS' snapshot facilities.

AUTHORS: Manuel Domínguez López. See AUTHORS file.

LICENSE: GPLv3+. Read LICENSE file.

"""

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
            self.frequency = toseconds(settings[name]['frequency'])
            self.quota = settings[name].getint('quota')
            self.readonly = settings[name].getboolean('readonly')
        else:
            clean_exit('No section in config file: ' + name, 8)

        self.name = name  # The name of section in config file (a path).
        self.sformat = '%Y-%m-%d %H:%M:%S'

    def snapshot_list(self):
        try:
            l = os.listdir(self.name)
        except FileNotFoundError:
            clean_exit(
                'ERROR: In can not found the directory: ' + self.name, 4)
        return(l)

    def print_snapshot_list(self):
        for i in self.snapshot_list():
            print(i)

    def print_properties(self):
        print('subvolume =', self.subvolume + '\n' +
              'frequency =', str(self.frequency) + '\n' +
              'quota =', str(self.quota) + '\n' +
              'readonly =', self.readonly)

    def print_snapshot_path_list(self):
        for i in self.snapshot_list():
            print(os.path.join(self.name, i))

    def info(self):
        list_s = self.snapshot_list()
        total_s = str(len(list_s))
        newer_s = list_s[0]
        older_s = list_s[-1]
        qperc = str(round(int(total_s) * 100 / int(self.quota), 2))
        print(
            'Snapshots:', total_s, '/', str(self.quota) +
            '\nQuota:', qperc, '%' +
            '\nNewer:', newer_s +
            '\nOlder:', older_s
            )

    def snapshot_list_len(self):
        return(len(self.snapshot_list()))

    def newer_snapshot(self):
        return(self.snapshot_list()[-1])

    def older_snapshot(self):
        return(self.snapshot_list()[0])

    def path_older_snapshot(self):
        return(os.path.join(self.name, self.older_snapshot()))

    def path_newer_snapshot(self):
        return(os.path.join(self.name, self.newer_snapshot()))

    def quota_diff(self):
        return(self.snapshot_list_len() - self.quota)

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
        self.delete(self.name)

    def clean_quota(self):
        quota_diff = self.quota_diff()
        if quota_diff > 0:
            for i in range(quota_diff):  # 0..quota_diff - 1
                self.delete(self.path_older_snapshot())

    def makesnapshot(self):
        try:
            if not os.path.isdir(self.name):
                cmd = ('btrfs', 'subvolume', 'create', self.name)
                subprocess.call(cmd, stdout=DEVNULL)
                #os.makedirs(self.name, exist_ok=True)
        except PermissionError:
            clean_exit('ERROR: I can not create the directory: ' +
                       self.name, 5)
        self.clean_quota()
        if self.snapshot_list_len() == 0:  # Make a copy if directory is empty.
            self.write()
        else:
            # Make a copy if newer copy is older than minage.
            diff = self.ts(self.now()) - self.ts(self.newer_snapshot())
            if diff > self.frequency:
                if self.quota_diff() == 0:  # Make room for a new snapshot.
                    self.delete(self.path_older_snapshot())
                self.write()

    def start(self):
        while True:
            self.makesnapshot()
            time.sleep(self.frequency)

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
            prog='snapman',
            description='A Btrfs snapshots manager'
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
                        help='Set verbosity on')
    
    parser.add_argument('--section-list', default=False, action='store_true',
                        help='Show the sections managed')
    parser.add_argument('--section-snapshot-list', default=None,
                        help='Show the list of snapshots taked from the section')
    parser.add_argument('--section-snapshot-path-list', default=None,
                        help='Show the list of paths to snapshots taked from the section')
    parser.add_argument('--section-snapshot-clean', default=None,
                        help='Delete all snapshots taked from the section')
    parser.add_argument('--section-info', default=None,
                        help='Show some information about the section status')
    parser.add_argument('--section-properties', default=None,
                        help='Print out the properties configured for the section')
    
    parser.add_argument('--subvolume-list', default=False, action='store_true',
                        help='Show a list of all subvolumes managed by configuration file')
    parser.add_argument('--subvolume-snapshot-list', default=None,
                        help='Show a list of all snapshots taked from the given subvolume')
    parser.add_argument('--subvolume-snapshot-clean', default=None,
                        help='Delete all snapshots taked from given subvolume')
    parser.add_argument('--subvolume-info', default=None,
                        help='Show some information about the subvolume status')
    
    parser.add_argument('--snapshot-info', default=None,
                        help='Show some information about the snapshot status')

    if not os.path.exists(parser.parse_args().configfile):
        clean_exit('ERROR: I can not find the configuration file.', 1)

    return(parser.parse_args())


def get_settings(args):
    ''' Get settings from config file. Overwrited by command line options. '''
    # FIXME: Need to validate settings
    settings = configparser.ConfigParser()
    # Get settings from args.configfile.
    settings.read(args.configfile)

    # For warnings if troubles with the config file:
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


def daemon(settings):
    for i in settings.sections():
        x = Section(i)
        x.daemonize()


def run_once(settings):
    for i in settings.sections():
        x = Section(i)
        x.makesnapshot()


def main():
    global settings
    global args

    args = parseargs()
    settings = get_settings(args)

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

    elif args.section_list:
        for i in settings.sections():
            print(i)
    elif args.section_snapshot_list:
        s = args.section_snapshot_list.rstrip('/')
        x = Section(s)
        x.print_snapshot_list()
    elif args.section_snapshot_path_list:
        s = args.section_snapshot_path_list.rstrip('/')
        x = Section(s)
        x.print_snapshot_path_list()
    elif args.section_snapshot_clean:
        s = args.section_snapshot_clean.rstrip('/')
        x = Section(s)
        x.snapshot_clean()
    elif args.section_info:
        s = args.section_info.rstrip('/')
        x = Section(s)
        x.info()
    elif args.section_properties:
        s = args.section_properties.rstrip('/')
        x = Section(s)
        x.print_properties()
    elif args.subvolume_list:
        l = []
        for s in settings.sections():
            l.append(settings[s]['subvolume'])
        for i in sorted(set(l)):
            print(i)

    elif args.subvolume_snapshot_list:
        sub = args.subvolume_snapshot_list
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        for i in settings.sections():
            if sub == settings[i]['subvolume']:
                found = True
                x = Section(i)
                x.print_snapshot_path_list()
        if not found:
            clean_exit('No section manages the subvolume: ' + sub, 6)

    elif args.subvolume_snapshot_clean:
        sub = args.subvolume_snapshot_clean
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
        clean_exit('SORRY: Not implemented yet :-P', 10)
    elif args.snapshot_info:
        clean_exit('SORRY: Not implemented yet :-P', 10)
        sub = args.snapshot_info
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')
        sub = os.path.dirname(sub)  # Corrected dirname return /foo from /foo/
        found = False
        for i in settings.sections():
                x = Section(i)
                if sub in x.print_snapshot_path_list():
                    found = True
                    print(x.name)
        if not found:
            clean_exit('No section manages the subvolume: ' + sub, 6)

    elif args.daemon:
        daemon(settings)
    else:
        run_once(settings)


if __name__ == '__main__':
    main()
    clean_exit()
