import time
import datetime
import subprocess
import threading
import Snapman.settings

from Snapman.args import args
from Snapman.quit import *  # include os, sys


settings = Snapman.settings.Settings(args.configfile)


class Snapshot():
    info_path = "Path"
    info_section = "Section"
    info_subvolume = "Subvolume"
    info_wday = "Wday"
    info_date = "Date"
    info_time = "Time"
    info_timestamp = "Timestamp"

    def __init__(self, path, ts):
        date = os.path.basename(path)
        date = int(datetime.datetime.strptime(date, ts).strftime("%s"))
        date = str(
            datetime.datetime.fromtimestamp(date).strftime('%A %F %T %s'))

        self.wday, self.date, self.time, self.ts = date.split()
        self.path = path
        self.timestamp = ts

    def get_generation(self):
        cmd = ('btrfs', 'subvolume', 'show', self.path)
        generation = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        for i in generation.communicate()[0].decode().split('\n'):
            if 'Generation' == i.split(':')[0].strip():  # key is 'Generation'
                return(i.split(':')[1].strip())  # value of the key
        return(None)


class Section():
    ''' The Section class represents a individual section in config file. '''
    info_name = 'section'
    info_subvolume = 'subvolume'
    info_count = 'snapshots'
    info_quota = 'quota'
    info_frequency = 'frequency'
    info_newer = 'newer'
    info_older = 'older'
    info_readonly = 'readonly'
    info_enabled = 'enabled'
    info_timestamp = 'timestamp'
    info_umask = 'umask'

    def __init__(self, section):
        self.noaccess = False

        self.name = section.name  # The name of section in configfile (a path).

        self.subvolume = section['subvolume']
        self.frequency = section['frequency']
        self.quota = section.getint('quota')
        self.readonly = section.getboolean('readonly')
        self.enabled = section.getboolean('enabled')
        self.timestamp = section['timestamp']
        self.umask = section['umask']

        if args.verbose:
            self.stdout = subprocess.STDOUT
            self.stderr = subprocess.STDOUT
        else:
            self.stdout = subprocess.DEVNULL
            self.stderr = subprocess.DEVNULL

        self.snapshot_list()  # Changes self.noaccess value
        self.getFrequency_sec()  # Gets self.frequency_sec

    def getFrequency_sec(self):
        '''Read minutes, hours, days or years and converts it to seconds.'''
        period = str(self.frequency)
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
            clean_exit('ERROR:I do not know how to convert ' + period +
                       ' to seconds', BADFREQ)
        fperiod = int(fperiod)
        if period.endswith('m'):
            fperiod = fperiod * 60
        elif period.endswith('h'):
            fperiod = fperiod * 60 * 60
        elif period.endswith('d'):
            fperiod = fperiod * 60 * 60 * 24
        elif period.endswith('y'):
            fperiod = fperiod * 60 * 60 * 24 * 365

        self.frequency_sec = fperiod

    def snapshot_list(self):
        '''
        Sets:
            self.noaccess
            self.snapshots
            self.snapshot_paths
            self.nsnapshots
            self.count
            self.percent
        '''
        try:
            self.snapshots = os.listdir(self.name)
        except FileNotFoundError:
            self.snapshots = []
        except PermissionError:
            self.noaccess = True
            self.snapshots = []
            print('No permission to scan section: ' + self.name,
                      file=sys.stderr)
        self.snapshot_paths = list(map(lambda x: os.path.join(self.name, x),
                                       self.snapshots))
        self.nsnapshots = self.nsnapshots()
        self.count = self.count()
        self.percent = self.percent()

    def count(self):
        return(str(self.nsnapshots) + ' / ' + str(self.quota))

    def snapshot_info(self, snap, printout=True):
        if snap in self.snapshot_paths:
            x = Snapshot(snap, self.timestamp)
            if printout:
                print(x.info_section + ':', self.name,
                      '\n' + x.info_subvolume + ':', self.subvolume,
                      '\n' + x.info_wday + ':', x.wday,
                      '\n' + x.info_date + ':', x.date,
                      '\n' + x.info_time + ':', x.time,
                      '\n' + x.info_timestamp + ':', x.ts)
            return(x)
        return(False)

    def print_snapshots(self, path=True):
        snaps = self.snapshot_paths
        if self.noaccess:
            return(False)
        for i in snaps:
            print(i)

    def print_properties(self):
        propk = (self.info_subvolume, self.info_frequency, self.info_quota,
                 self.info_readonly, self.info_enabled, self.info_timestamp,
                 self.info_umask)
        propv = (self.subvolume, self.frequency, self.quota,
                 self.readonly, self.enabled, self.timestamp, self.umask)
        print('[' + self.name + ']')
        for i in range(len(propk)):
            if args.verbose:
                print(propk[i], '=', propv[i])
            else:
                if settings.config['DEFAULT'][propk[i]] != str(propv[i]):
                    print(propk[i], '=', propv[i])

    def percent(self):
        n = self.nsnapshots
        if n == 'unknown':
            return(n)
        return(str(round(int(n) * 100 / self.quota)) + ' %')

    def info(self):
        if args.verbose:
            print(self.info_name + ':', self.name)
        print(
            self.info_subvolume + ':', self.subvolume +
            '\n' + self.info_count + ':', str(self.nsnapshots),
            '\n' + self.info_quota + ':', self.percent,
            '\n' + self.info_frequency + ':', self.frequency,
            '\n' + self.info_newer + ':', self.newer_snapshot(),
            '\n' + self.info_older + ':', self.older_snapshot(),
            '\n' + self.info_enabled + ':', self.enabled,
            '\n' + self.info_umask + ':', self.umask,
            )

    def restore(self, old, backup=True):
        '''
        Restore(old, backup=True)
                snap sub
                del sub && snap old sub
                '''
        #if self.delete(self.subvolume):



    def nsnapshots(self):
        snaps = self.snapshot_paths
        if self.noaccess:
            return('unknown')
        return(len(self.snapshot_paths))

    def newer_snapshot(self, fullpath=True):
        ts = 0
        newer = ''
        for i in self.snapshots:
            aux = self.ts(i)
            if ts < aux:
                ts = aux
                newer = i
        if fullpath:
            if newer:
                return(os.path.join(self.name, newer))
        return(newer)  # Must be None?

    def older_snapshot(self, fullpath=True):
        ts = 0
        older = ''
        for i in self.snapshots:
            aux = self.ts(i)
            if ts == 0 or ts > aux:
                ts = aux
                older = i
        if fullpath:
            if older:
                return(os.path.join(self.name, older))
        return(older)

    def has_changed(self):
        ''' Return True if section has changed respect his newer snapshot. '''
        src = Snapshot(self.subvolume)
        newer = Snapshot(self.newer_snapshot())

        if not newer:
            return(True)  # No snapshots means that section has changes

        cmd = ('btrfs', 'subvolume', 'find-new', src.path,
               newer.get_generation())
        diff = subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)

        for i in diff.communicate()[0].decode().split('\n'):
            if i.startswith('inode'):
                return(True)  # Has changed
            else:
                return(False)

    def quota_diff(self):
        n = self.nsnapshots
        if n == 'unknown':  # No permission to list snapshot in section
            return(-1)  # Switch off makesnapshot()
        return(n - self.quota)

    def now(self):
        return(datetime.datetime.now().strftime(self.timestamp))

    def ts(self, t):
        try:
            d = datetime.datetime.strptime(t, self.timestamp)
        except ValueError:
            clean_exit('ERROR: Bad format found in ' +
                       os.path.join(self.name, t), BADTS)
        return(time.mktime(d.timetuple()))

    def write(self):
        dest = os.path.join(self.name, self.now())
        if self.readonly:
            cmd = ('btrfs', 'subvolume', 'snapshot', '-r',
                   self.subvolume, dest)
        else:
            cmd = ('btrfs', 'subvolume', 'snapshot', self.subvolume, dest)
        if subprocess.run(cmd,
                          stdout=self.stdout, stderr=self.stderr).returncode:
            return(False)
        return(True)

    def delete(self, svol):
        cmd = ('btrfs', 'subvolume', 'delete', svol)
        if subprocess.run(cmd,
                          stdout=self.stdout, stderr=self.stderr).returncode:
            return(False)
        return(True)

    def delete_and_write(self):
        status = True
        if self.quota_diff() == 0:  # Make room for a new snapshot.
            if not self.delete(self.older_snapshot()):
                status = False
        if not self.write():
            status = False
        return(status)

    def snapshot_clean(self):
        if not os.path.exists(self.name):
            return(True)
        snaps = self.snapshot_paths
        if self.noaccess:
            return(False)
        for i in snaps:
            s = os.path.join(self.name, i)
            self.delete(s)
        # self.name will be full deleted or return False
        try:
            os.rmdir(self.name)
        except:
            return(False)
        return(True)

    def clean_quota(self):
        status = True
        quota_diff = self.quota_diff()  # Only calculate one time
        if quota_diff > 0:  # Not >= 0, for match quota with number of copies
            for i in range(quota_diff):  # from 0 to (quota_diff - 1)
                if not self.delete(self.older_snapshot()):
                    status = False
        return(status)

    def makesnapshot(self, force=False):
        # Return if source subvolume not exists:
        if not os.path.exists(self.subvolume):
            print('WARNING in section', self.name +
                  ': Subvolume', self.subvolume, 'does not exist',
                  file=sys.stderr)
            return(False)

        # Only do actions if enabled property is on:
        if not self.enabled:
            if args.verbose:
                print('WARNING: Section', self.name, 'is disabled',
                      file=sys.stderr)
            return(False)

        try:
            os.umask(int(self.umask, 8))
            os.makedirs(self.name, exist_ok=True)
        except:
            return(False)

        if not self.clean_quota():
            return(False)

        if self.nsnapshots == 0:
            # Make a copy if directory is empty.
            if not self.write():
                return(False)
        elif force:
            # Force new copy
            if not self.delete_and_write():
                return(False)
        else:
            # Make a copy if time difference inter new copy and last copy is
            # higher than configured frequency.
            now = self.ts(self.now())
            newer = self.ts(self.newer_snapshot(False))
            diff = now - newer
            if diff > self.frequency_sec:
                if self.has_changed():
                    if not self.delete_and_write():
                        return(False)
        return(True)

    # Daemonizing:
    def start(self):
        while True:
            if args.verbose:
                print("Snapshotting", self.name,
                      "every", self.frequency_sec, "seconds")
            # self.reload()  # Re-read configfile for update properties
            self.makesnapshot()
            time.sleep(self.frequency_sec)

    def daemonize(self):
        threading.Thread(target=self.start).start()
