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

class Snapshot():
    ''' Class for store snapshot directories.
    Accepts string in "2016-01-12 17:10:30" format '''
    def __init__(self, date):
        self.sformat = "%Y-%m-%d %H:%M:%S"
        self.name = date
        try:
            self.ts = time.mktime(
                    datetime.datetime.strptime(
                        self.name, self.sformat).timetuple()
                    )
        except ValueError:
            clean_exit(
                    'Invalid format:', self.name,
                    'does not match with', self.sformat,
                    3
                    )

    def write(self, orig, dest):
        dest = os.path.join(dest, self.name)
        cmd = ('btrfs', 'subvolume', 'snapshot', orig, dest)
        subprocess.call(cmd, stdout=DEVNULL)

    def delete(self, dest):
        dest = os.path.join(dest, self.name)
        cmd = ('btrfs', 'subvolume', 'delete', dest)
        subprocess.call(cmd, stdout=DEVNULL)


class Unit():
    ''' The Unit class represents a individual section in config file. '''
    def __init__(self, name, store, subvolume, readonly, directories):
        self.name = name
        self.store = store
        self.subvolume = subvolume
        self.readonly = readonly

        self.directories = {}
        for d in directories.split(','):
            dirname, minage, quota = d.split(':')
            dirname = dirname.strip()
            self.directories.update(
                    {
                        dirname: {
                            'minage': toseconds(minage), 'quota': int(quota)
                            }
                        }
                    )


def toseconds(period):
    '''Read minutes, hours, days or years and converts it to seconds.'''
    period = str(period)
    if period.endswith('m'):
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
        clean_exit('I do not know how to convert ' + period + ' to seconds', 2)
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
    daemon = False  # Daemon mode.
    sample = False  # Print sample config file to stdout and exits.
    purge = False  # Purge snapshots.
    pidfile = None  # Write pidfile

    parser = argparse.ArgumentParser(
            prog='Time Back',
            description='A Btrfs based backup system'
            )

    parser.add_argument('-c', '--configfile', default=configfile)
    parser.add_argument('-s', '--sample', default=sample, action='store_true')
    parser.add_argument('-d', '--daemon', default=daemon, action='store_true')
    parser.add_argument('--pidfile', default=pidfile)
    parser.add_argument('--purge', default=purge, action='store_true')

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
        print(
                'WARNING: \'' + args.configfile + '\' is a directory.',
                'Fallback to default settings.',
                file=sys.stderr
                )
    except FileNotFoundError:
        print(
                'WARNING: \'' + args.configfile + '\' does not exists.',
                'Fallback to default settings.',
                file=sys.stderr
                )
    except IOError:
        print(
                'WARNING: I/O error loading config file: \'' +
                args.configfile + '\'.', 'Fallback to default settings.',
                file=sys.stderr
                )
    except:
        print(
                'WARNING: Unknown error loading config file: \'' +
                args.configfile + '\'. Fallback to default settings.',
                file=sys.stderr
                )
    else:
        f.close()

    return(settings)


def makecopy(settings, purge=False):
    ''' Make or delete a copy if necessary. '''
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new = Snapshot(now)
    for section in settings.sections():
        unit = Unit(
            section,
            settings[section]['store'],
            settings[section]['subvolume'],
            settings[section]['readonly'],
            settings[section]['directories']
            )
        for freq in unit.directories.keys():
            minage = unit.directories[freq]['minage']
            quota = unit.directories[freq]['quota']
            dname = os.path.join(unit.store, unit.name)
            dfreq = os.path.join(dname, freq)
            subvolume = unit.subvolume

            try:
                os.makedirs(dfreq, exist_ok=True)
            except PermissionError:
                print('ERROR: In can not make the directory:', dfreq,
                      file=sys.stderr)

            try:
                copies = os.listdir(dfreq)
            except FileNotFoundError:
                print('ERROR: In can not found the directory:', dfreq,
                      file=sys.stderr)

            copies.sort()
            ncopies = len(copies)
            quota_diff = ncopies - quota

            if purge:
                for i in range(ncopies):
                    oldcopy = Snapshot(copies[i])
                    oldcopy.delete(dfreq)
                os.removedirs(dfreq)
            else:
                for i in range(quota_diff):  # 0..quota_diff - 1
                    oldcopy = Snapshot(copies[i])
                    oldcopy.delete(dfreq)
                    copies.pop(i)

                if ncopies == 0:  # Make a copy if directory is empty.
                    new.write(subvolume, dfreq)
                else:
                    # Make a copy if last copy is older than minage.
                    lastcopy = Snapshot(copies[-1])
                    if new.ts - lastcopy.ts > minage:
                        quota_diff = len(copies) - quota
                        if quota_diff == 0:  # Make room for a new snapshot.
                            oldercopy = Snapshot(copies[0])
                            oldercopy.delete(dfreq)
                            copies.pop(0)
                        new.write(subvolume, dfreq)


def daemon(settings):
    frequencies = []
    minfreq = []
    for i in settings.sections():
        for j in settings[i]['directories'].split(','):
            dirname, minage, quota = j.split(':')
            frequencies.append(minage)

    for i in frequencies:
        minfreq.append(toseconds(i))

    minfreq = sorted(minfreq).pop(0)
    makecopy(settings)
    time.sleep(minfreq)


def clean_exit(text=None, exitnum=0):
    if text:
        print(text, file=sys.stderr)
    try:
        os.remove(pidpath)
    except NameError:
        exit(exitnum)
    exit(exitnum)


def main():

    args = parseargs()
    settings = get_settings(args)

    if args.pidfile:
        global pidpath
        pidpath = args.pidfile
        PID = os.getpid()
        pidfile = open(pidpath, 'w')
        pidfile.write(str(PID))
        pidfile.close()


    if args.sample:
        print('''\
# This is the config file for snapman.py. It will be parsed by configparser
# python module.
# Copy this file in /etc/snapman.ini and edit it at your preferences.
# You can also set an alternative config file with -c command line option.
# Command line setted options will overwrite this settings.

[DEFAULT]
# Default values for all sections.
# The directory where were stored the snapshots.
#store = /.snapman
# Full path to subvolume to copy.
subvolume = /
# Directories in name:minage[m|h|d|y]:quota format (comma separated).
directories = 15m:15m:4, 60m:60m:24, diaria:24h:30, semanal:10y:48
# True for a readonly copy.
readonly = false
''')
    if args.purge:
        makecopy(settings, args.purge)
    elif args.daemon:
        while True:
            try:
                daemon(settings)
            except KeyboardInterrupt:
                clean_exit(None, 130)
    else:
        makecopy(settings)


if __name__ == '__main__':
    main()
    clean_exit()
