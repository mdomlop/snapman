import configparser
from Snapman.quit import BADCONFIG, clean_exit


class Settings():
    def __init__(self, configfile):
        # Exit if there are troubles with the configuration file:
        try:
            f = open(configfile, "r")
            f.close()
        except IsADirectoryError:
            clean_exit('ERROR: \'' + configfile + '\' is a directory.',
                       BADCONFIG)
        except FileNotFoundError:
            clean_exit('ERROR: \'' + configfile + '\' does not exists.',
                       BADCONFIG)
        except IOError:
            clean_exit('ERROR: I/O error loading config file: \'' +
                       configfile, BADCONFIG)
        except:
            clean_exit('ERROR: Unknown error while loading config file: \'' +
                       configfile, BADCONFIG)

        self.config = configparser.ConfigParser(interpolation=None)  # for timestamp %
        self.config.read(configfile)
        self.sections = self.config.sections()
