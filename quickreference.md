Quick reference
----------------


### Sections

1. To show a list of all sessions in config file

        snapman --section-list
        /backups/OS
        /backups/OS2
        /backups/OS3
        /pools/DATOS/Copias/Biblioteca
        /pools/DATOS/Copias/Casa
        /pools/DATOS/Copias/Fotos
        /pools/DATOS/Copias/demonio


snapman --section-snapshot-list /backups/OS
20171016-002413
20171016-022413
20171016-042413
20171016-062414

snapman --section-snapshot-path-list /backups/OS
/backups/OS/20171016-002413
/backups/OS/20171016-022413
/backups/OS/20171016-042413
/backups/OS/20171016-062414

snapman --section-info /backups/OS 
Snapshots 4 / 30
Quota 13.33 %
Newer 20171016-002413
Older 20171016-062414

snapman --section-properties /backups/OS 
subvolume = /
frequency = 86400
quota = 30
readonly = True

snapman --section-snapshot-clean /backups/OS --verbose
Delete subvolume (no-commit) '/backups/OS/20171016-002413'
Delete subvolume (no-commit) '/backups/OS/20171016-022413'
Delete subvolume (no-commit) '/backups/OS/20171016-042413'
Delete subvolume (no-commit) '/backups/OS/20171016-062414'
Delete subvolume (no-commit) '/backups/OS'

### Subvolumes

snapman --subvolume-list
/
/pools/DATOS/Biblioteca
/pools/DATOS/Casa
/pools/DATOS/Fotos
/pools/DATOS/Usuarios/demonio

snapman --subvolume-snapshot-list /
/backups/OS/20171016-002413
/backups/OS/20171016-022413
/backups/OS/20171016-042413
/backups/OS/20171016-062414


snapman --subvolume-snapshot-clean /data/documents --verbose

snapman --subvolume-info /data/documents
Size 1 Gib
Snapshots 12
Last /data/snapman/documents/20171011-142007 (1 hour ago)
Older /data/snapman/documents/20170409-140700 (12 days ago)

------------------------------------------------


snapman --snapshot-info /datos/snapman/movies
size 10 Gib
diff -3 Gib
Age 2 weeks
Subvolume /datos/movies

