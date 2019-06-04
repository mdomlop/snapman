import sys
import os
import Snapman.args

NORMAL = 0
BADCOM = Snapman.args.BADCOM
BADCONFIG = 2
BADSECT = 3
BADSNAP = 4
BADSUB = 5
BADFREQ = 6
BADTS = 7
BADDIR = 8
BADPID = 9
BADPERM = 10
KBINT = 130


def clean_exit(text=None, exitnum=NORMAL):
    if text:
        print(text, file=sys.stderr)
    if Snapman.args.pidfile:
        try:
            os.remove(Snapman.args.pidfile)
        except:
            print('Failed to remove pidfile:', Snapman.args.pidfile,
                    file=sys.stderr)
            sys.exit(BADPID)
    sys.exit(exitnum)
