import sys
from Snapman.program_info import PROGRAM_NAME, DESCRIPTION, VERSION

BADCOM = 1

# Default values:
defconfigfile = '/etc/snapman.ini'  # Configuration file
defcommand = 'list'

# Failsafe:
command = None
targets = None

#args = sys.argv[:]  # Preserve sys.argv for QApplication(sys.argv)
#executable = args.pop(0)


def split_arg(opt, start=1):
    ''' Split options in git-style mode. '''
    n = len(opt)  # The number of chars in option
    c = list(opt)  # Get all chars of the option 
    s = opt[:start] # Start point
    l = [s]  # First element in list from start point

    for i in range(start, n):
        s = (s + c[i])
        l.append(s)
    return(l)


def check_opt(elements):
    for i in elements:
        if i in sys.argv:
            return(sys.argv.index(i))  # Must be > 0
    return(False)


def check_extra(element):
    try:
        sys.argv[element + 1]
        return(True)
    except IndexError:
        return(False)


def get_extra(element):
    if check_extra(element):
        command = sys.argv[element + 1]
    else:
        command = defcommand

    if check_extra(element + 1):
        targets = sys.argv[element + 1:]
    else:
        if command != defcommand:
            print(command)
            fail('Please, provide a target.', BADCOM)



def fail(text=None, exitnum=BADCOM):
    if text:
        print(text, file=sys.stderr)
    sys.exit(exitnum)

# Exclusive options:
version_arg = ('-V', '--version')
help_arg = ('-h', '--help')
sample_arg = ('-s', '--sample')

# Semi-exclusive options
daemon_arg = ('-d', '--daemon')
gui_arg = ('-g', '--gui')

# Modifiers:
verbose_arg = ('-v', '--verbose')
configfile_arg = ('-c', '--configfile')
pidfile_arg = ('-p', '--pidfile')

# Commands:
list_arg = split_arg('list')
clean_arg = split_arg('clean')
information_arg = split_arg('information')
properties_arg = split_arg('properties')
newsnapshot_arg = split_arg('newsnapshot')

# Options:
sections_arg = split_arg('sections', 2)
subvolumes_arg = split_arg('subvolumes', 2)
snapshots_arg = split_arg('snapshots', 2)


# Assign index of option in sys.argv. If not found value were be 0 (False)
version = check_opt(version_arg)
help = check_opt(help_arg)
sample = check_opt(sample_arg)

daemon = check_opt(daemon_arg)
gui = check_opt(gui_arg)

verbose = check_opt(verbose_arg)
configfile = check_opt(configfile_arg)
pidfile = check_opt(pidfile_arg)

list = check_opt(list_arg)
clean = check_opt(clean_arg)
information = check_opt(information_arg)
properties = check_opt(properties_arg)
newsnapshot = check_opt(newsnapshot_arg)

sections = check_opt(sections_arg)
subvolumes = check_opt(subvolumes_arg)
snapshots = check_opt(snapshots_arg)

if configfile:
    if check_extra(configfile):
        configfile = sys.argv[configfile + 1]
    else:
        fail('Please, provide a configuration file path.', BADCOM)
else:
    configfile = defconfigfile

if pidfile:
    if check_extra(pidfile):
        pidfile = sys.argv[pidfile + 1]
    else:
        fail('Please, provide a pidfile path.', BADCOM)

if sections:
    get_extra(sections)
elif subvolumes:
    get_extra(subvolumes)
elif snapshots:
    get_extra(snapshots)

