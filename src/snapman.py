#!/usr/bin/env python3

import Snapman.functions
from Snapman.args import args
from Snapman.quit import clean_exit


def main():
    if args.pidfile:
        Snapman.functions.pidfile()
    if args.sample:
        Snapman.functions.sample()
    elif args.sections:
        Snapman.functions.sections()
    elif args.section_snapshots:
        Snapman.functions.section_snapshots()
    elif args.section_newsnapshot:
        Snapman.functions.section_newsnapshot()
    elif args.section_clean:
        Snapman.functions.section_clean()
    elif args.section_info:
        Snapman.functions.section_info()
    elif args.section_properties:
        Snapman.functions.section_properties()
    elif args.subvolumes:
        Snapman.functions.subvolumes()
    elif args.subvolume_snapshots:
        Snapman.functions.subvolume_snapshots()
    elif args.subvolume_sections:
        Snapman.functions.subvolume_sections()
    elif args.subvolume_clean:
        Snapman.functions.subvolume_clean()
    elif args.subvolume_info:
        Snapman.functions.subvolume_info()
    elif args.snapshots:
        Snapman.functions.snapshots()
    elif args.snapshot_info:
        Snapman.functions.snapshot_info()
    elif args.gui:
        Snapman.functions.gui()
    elif args.daemon:
        Snapman.functions.daemon()
    else:
        Snapman.functions.run_once()


if __name__ == '__main__':
    main()
    clean_exit()
