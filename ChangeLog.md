CHANGELOG
---------

- *Release 0.9b* (2017-10-26):
    - Renamed project to Snapman.
    - Better format for configuration file.
    - Multi-thread daemon mode.
    - Removed `--purge` command line option. Improved options are available.
    - Added new commad line options.
    - Updated man pages.
- *Release 0.2* (2017-07-14):
    - Change ronn for pandoc for building man pages.
    - Completed documentation in english. Deleted documentation in spanish.
    - Added `--pidfile` command line option.
    - Added `--purge` command line option.
    - Added daemon mode by `--daemon` command line option. Now you don't need
    any systemd timer.
    - Added `--sample` command line option for print sample config file to
    stdout.
    - Removed harcoded default settings. Program will fail if config file not
    exist.
    - Removed `--verbose` command line option.
    - Removed `ignore` setting. I you want to ignore a secion of configuration
    file you must to comment it.
- *Release 0.1* (2016-02-07 12:30):
    - Initial stable version.
