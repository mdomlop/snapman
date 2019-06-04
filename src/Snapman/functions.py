from Snapman.program_info import SAMPLE, PROGRAM_NAME, USAGE, VERSION
from Snapman.section import Section, settings
import Snapman.args
from Snapman.quit import *  # include os, sys


def check_root():
    if os.geteuid() != 0:
        return(False)
    return(True)


def usage():
    print('Usage:', PROGRAM_NAME, USAGE)


def sample():
    print(SAMPLE)

def version():
    print(PROGRAM_NAME, VERSION)

def gui():
    import Snapman.gui
    Snapman.gui.run()


def daemon():
    if not check_root():
        clean_exit(
'''You need to have root privileges to execute this script in daemon mode.
Please try again, this time using "sudo". Exiting.''', BADPERM)

    for i in settings.sections:
        x = Section(settings.config[i])
        x.daemonize()


def run_once():
    if not check_root():
        clean_exit(
'''You need to have root privileges to execute this script.
Please try again, this time using "sudo". Exiting.''', BADPERM)

    for i in settings.sections:
        x = Section(settings.config[i])
        x.makesnapshot()


def pidfile():
    PID = os.getpid()
    pidfile = open(Snapman.args.pidfile, 'w')
    try:
        pidfile.write(str(PID))
        pidfile.close()
    except:
        clean_exit('Failed to create pidfile:', Snapman.args.pidfile, BADPID)


def sections():
    if not Snapman.args.verbose:
        for i in settings.sections:
            print(i)
    else:
        for i in settings.sections:
            x = Section(settings.config[i])
            r = 'readonly' if x.readonly else 'writable'
            print(x.name + ':',
                  str(x.snapshot_count()) + '/' + str(x.quota),
                  r, 'from', x.subvolume)


def section_snapshots():
    for i in Snapman.args.targets:
        s = i.rstrip('/')
        x = Section(settings.config[s])
        if Snapman.args.verbose:
            for i in x.snapshot_paths:
                print(i, 'from', x.subvolume)
        else:
            x.print_snapshots()


def section_newsnapshot():
    for i in Snapman.args.targets:
        s = i.rstrip('/')
        x = Section(settings.config[s])
        x.makesnapshot(True)


def section_clean():
    for i in Snapman.args.targets:
        s = i.rstrip('/')
        x = Section(settings.config[s])
        x.snapshot_clean()


def section_info():
    for i in Snapman.args.targets:
        s = i.rstrip('/')
        x = Section(settings.config[s])
        x.info()
        print()


def section_properties():
    for i in Snapman.args.targets:
        s = i.rstrip('/')
        x = Section(settings.config[s])
        x.print_properties()
        print()


def subvolumes():
    l = []
    for s in settings.sections:
        l.append(settings.config[s]['subvolume'])
    for i in sorted(set(l)):
        print(i)


def subvolume_snapshots():
    for sub in Snapman.args.targets:
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        for i in settings.sections:
            if sub == settings.config[i]['subvolume']:
                found = True
                x = Section(settings.config[i])
                if not Snapman.args.verbose:
                    x.print_snapshots()
                else:
                    for s in x.snapshot_paths:
                        print(s, 'from', x.subvolume)
        if not found:
            clean_exit('Currently there is no snapshot for the subvolume: ' +
                       sub, BADSUB)


def subvolume_sections():
    for sub in Snapman.args.targets:
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        for i in settings.sections:
            if sub == settings.config[i]['subvolume']:
                found = True
                x = Section(settings.config[i])
                if not Snapman.args.verbose:
                    print(x.name)
                else:
                    print(x.name + ':', x.snapshot_count())
        if not found:
            clean_exit('No section manages the subvolume: ' + sub, BADSUB)


def subvolume_clean():
    for sub in Snapman.args.targets:
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        for i in settings.sections:
            if sub == settings.config[i]['subvolume']:
                found = True
                x = Section(settings.config[i])
                x.snapshot_clean()
        if not found:
            clean_exit('No section manages the subvolume: ' + sub, BADSUB)


def subvolume_info():
    for sub in Snapman.args.targets:
        if sub != '/':  # Prevent strip filesystem root.
            sub = sub.rstrip('/')

        found = False
        snap = []
        sect = []
        for i in settings.sections:
            if sub == settings.config[i]['subvolume']:
                found = True
                x = Section(settings.config[i])
                snap += x.snapshot_paths
                sect.append(x.name)

        if not found:
            clean_exit('No section manages the subvolume: ' + sub, BADSUB)
        if snap:
            sort_snaps = sorted(snap)
            newer = sort_snaps[0]
            older = sort_snaps[-1]
        else:
            newer = ''
            older = ''
        if Snapman.args.verbose:
            print('Subvolume:', sub)
        print('Snapshots:', len(snap),
              '\nSections:', len(sect),
              '\nNewer:', newer,
              '\nOlder:', older)
        print()


def snapshots():
    for s in settings.sections:
        x = Section(settings.config[s])
        if Snapman.args.verbose:
            for i in x.snapshot_paths:
                print(i, 'from', x.subvolume)
        else:
            x.print_snapshots()


def snapshot_info():
    for snap in Snapman.args.targets:
        if snap != '/':  # Prevent strip filesystem root.
            snap = snap.rstrip('/')
        else:
            clean_exit("Root directory can't be a snapshot!", BADSNAP)
        found = 0
        for i in settings.sections:
            x = Section(settings.config[i])
            if x.snapshot_info(snap):
                found =+ 1
        if not found:
            clean_exit('No section manages the snapshot: ' + snap, BADSNAP)
