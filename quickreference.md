Quick reference:
----------------


### Sections:

1. To show a list of all sessions in config file:

        snapman --section-list
        /backups/OS
        /pools/DATOS/Copias/Biblioteca
        /pools/DATOS/Copias/Casa
        /pools/DATOS/Copias/Fotos
        /pools/DATOS/Copias/demonio


snapman --section-snapshot-list /backups/OS
2017-10-16 00:24:13
2017-10-16 02:24:13
2017-10-16 04:24:13
2017-10-16 06:24:14

snapman --section-snapshot-path-list /backups/OS
/backups/OS/2017-10-16 00:24:13
/backups/OS/2017-10-16 02:24:13
/backups/OS/2017-10-16 04:24:13
/backups/OS/2017-10-16 06:24:14

snapman --section-info /backups/OS 
Snapshots: 4 / 30
Quota: 13.33 %
Newer: 2017-10-16 00:24:13
Older: 2017-10-16 06:24:14

snapman --section-properties /backups/OS 
subvolume = /
frequency = 86400
quota = 30
readonly = True

snapman --section-snapshot-clean /backups/OS --verbose
Delete subvolume (no-commit): '/backups/OS/2017-10-16 00:24:13'
Delete subvolume (no-commit): '/backups/OS/2017-10-16 02:24:13'
Delete subvolume (no-commit): '/backups/OS/2017-10-16 04:24:13'
Delete subvolume (no-commit): '/backups/OS/2017-10-16 06:24:14'
Delete subvolume (no-commit): '/backups/OS'

### Subvolumes:

snapman --subvolume-list
/
/pools/DATOS/Biblioteca
/pools/DATOS/Casa
/pools/DATOS/Fotos
/pools/DATOS/Usuarios/demonio

snapman --subvolume-snapshot-list /
/backups/OS/2017-10-16 00:24:13
/backups/OS/2017-10-16 02:24:13
/backups/OS/2017-10-16 04:24:13
/backups/OS/2017-10-16 06:24:14


snapman --subvolume-snapshot-clean /data/documents

snapman --subvolume-info /data/documents
Size: 1 Gib
Snapshots: 12
Last: /data/snapman/documents/2017-10-11 14:20:07 (1 hour ago)
Older: /data/snapman/documents/2017-04-09 14:07:00 (12 days ago)

------------------------------------------------


snapman --snapshot-info /datos/snapman/movies
size: 10 Gib
diff: -3 Gib
Age: 2 weeks
Subvolume: /datos/movies

