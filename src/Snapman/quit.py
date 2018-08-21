import sys
import os
from Snapman.args import args

NORMAL = 0
BADCONFIG = 1
BADSECT = 2
BADSNAP = 3
BADSUB = 4
BADFREQ = 5
BADTS = 6
BADDIR = 7
BADPID = 8
KBINT = 130


def clean_exit(text=None, exitnum=NORMAL):
    if text:
        print(text, file=sys.stderr)
    if args.pidfile:
        try:
            os.remove(args.pidfile)
        except:
            print('Failed to remove pidfile:', args.pidfile, file=sys.stderr)
            sys.exit(BADPID)
    sys.exit(exitnum)
