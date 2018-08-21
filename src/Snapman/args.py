import argparse
from Snapman.program_info import PROGRAM_NAME, DESCRIPTION, VERSION


# Default options:
defconfigfile = '/etc/snapman.ini'  # Configuration file
defpidfile = None  # Writes pidfile.

parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description=DESCRIPTION
        )

parser.add_argument('-c', '--configfile', default=defconfigfile,
                    help='Alternative configuration file')
parser.add_argument('-p', '--pidfile', default=defpidfile,
                    help='Write a pidfile')
parser.add_argument('-s', '--sample', default=False, action='store_true',
                    help='Print out a sample configuration file')
parser.add_argument('-g', '--gui', default=False, action='store_true',
                    help='Execute in graphic mode')
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
parser.add_argument('--section-newsnapshot', default=None,
                    help='Force creation a new snapshot for the section')

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

args = parser.parse_args()
