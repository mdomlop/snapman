from Snapman.program_info import SAMPLE
from Snapman.section import Section, settings
from Snapman.args import args
from Snapman.quit import *  # include os, sys


def gui():
    import Snapman.gui
    Snapman.gui.run()


def daemon():
    for i in settings.sections:
        x = Section(settings.config[i])
        x.daemonize()


def run_once():
    for i in settings.sections:
        x = Section(settings.config[i])
        x.makesnapshot()


def pidfile():
    PID = os.getpid()
    pidfile = open(args.pidfile, 'w')
    try:
        pidfile.write(str(PID))
        pidfile.close()
    except:
        clean_exit('Failed to create pidfile:', args.pidfile, BADPID)


def sample():
    print(SAMPLE)


def sections():
    if not args.verbose:
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
    s = args.section_snapshots.rstrip('/')
    x = Section(settings.config[s])
    if args.verbose:
        for i in x.snapshot_paths:
            print(i, 'from', x.subvolume)
    else:
        x.print_snapshots()


def section_newsnapshot():
    s = args.section_newsnapshot.rstrip('/')
    x = Section(settings.config[s])
    x.makesnapshot(True)


def section_clean():
    s = args.section_clean.rstrip('/')
    x = Section(settings.config[s])
    x.snapshot_clean()


def section_info():
    s = args.section_info.rstrip('/')
    x = Section(settings.config[s])
    x.info()


def section_properties():
    s = args.section_properties.rstrip('/')
    x = Section(settings.config[s])
    if args.verbose:
        x.print_properties()
    else:
        x.print_properties()


def subvolumes():
    l = []
    for s in settings.sections:
        l.append(settings.config[s]['subvolume'])
    for i in sorted(set(l)):
        print(i)


def subvolume_snapshots():
    sub = args.subvolume_snapshots
    if sub != '/':  # Prevent strip filesystem root.
        sub = sub.rstrip('/')

    found = False
    for i in settings.sections:
        if sub == settings.config[i]['subvolume']:
            found = True
            x = Section(settings.config[i])
            if not args.verbose:
                x.print_snapshots()
            else:
                for s in x.snapshot_paths:
                    print(s, 'from', x.subvolume)
    if not found:
        clean_exit('Currently there is no snapshot for the subvolume: ' +
                   sub, BADSUB)


def subvolume_sections():
    sub = args.subvolume_sections
    if sub != '/':  # Prevent strip filesystem root.
        sub = sub.rstrip('/')

    found = False
    for i in settings.sections:
        if sub == settings.config[i]['subvolume']:
            found = True
            x = Section(settings.config[i])
            if not args.verbose:
                print(x.name)
            else:
                print(x.name + ':', x.snapshot_count())
    if not found:
        clean_exit('No section manages the subvolume: ' + sub, BADSUB)


def subvolume_clean():
    sub = args.subvolume_clean
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
    sub = args.subvolume_info
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
    if args.verbose:
        print('Subvolume:', sub)
    print('Snapshots:', len(snap),
          '\nSections:', len(sect),
          '\nNewer:', newer,
          '\nOlder:', older)


def snapshots():
    for s in settings.sections:
        x = Section(settings.config[s])
        if args.verbose:
            for i in x.snapshot_paths:
                print(i, 'from', x.subvolume)
        else:
            x.print_snapshots()


def snapshot_info():
    snap = args.snapshot_info
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
