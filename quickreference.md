Quick reference
----------------


### Sections

1. To show a list of all sessions in config file

snapman --sections
/backups/OS
/backups/debian
/backups/mdl
/pools/DATOS/Copias/Biblioteca
/pools/DATOS/Copias/Casa
/pools/DATOS/Copias/Fotos
/pools/DATOS/Copias/demonio

snapman --sections --verbose
/backups/OS: 1/30 readonly from /
/backups/debian: 4/30 readonly from /
/backups/mdl: 4/30 readonly from /
/pools/DATOS/Copias/Biblioteca: 0/30 readonly from /pools/DATOS/Biblioteca
/pools/DATOS/Copias/Casa: 0/30 readonly from /pools/DATOS/Casa
/pools/DATOS/Copias/Fotos: 0/30 readonly from /pools/DATOS/Fotos
/pools/DATOS/Copias/demonio: 0/30 readonly from /pools/DATOS/Usuarios/demonio

snapman --section-snapshots /backups/mdl
/backups/mdl/20171019-112455
/backups/mdl/20171021-072305
/backups/mdl/20171022-085634
/backups/mdl/20171023-144315


snapman --section-info /backups/mdl
Snapshots: 4/30
Quota: 7%
Newer: 20171023-144315
Older: 20171019-112455


snapman --section-properties /backups/mdl
subvolume = /
frequency = 1d
quota = 30
readonly = True

snapman --section-clean /backups/mdl --verbose
Delete subvolume (no-commit): '/backups/mdl/20171019-112455'
Delete subvolume (no-commit): '/backups/mdl/20171021-072305'
Delete subvolume (no-commit): '/backups/mdl/20171022-085634'
Delete subvolume (no-commit): '/backups/mdl/20171023-144315'
Delete subvolume (no-commit): '/backups/mdl'



### Subvolumes

snapman --subvolumes
/
/pools/DATOS/Biblioteca
/pools/DATOS/Casa
/pools/DATOS/Fotos
/pools/DATOS/Usuarios/demonio


snapman --subvolume-snapshots /
/backups/OS/20171023-151330
/backups/debian/20171019-112453
/backups/debian/20171021-072305
/backups/debian/20171022-085634
/backups/debian/20171023-144315



snapman --subvolume-clean / --verbose
Delete subvolume (no-commit): '/backups/OS/20171023-151330'
Delete subvolume (no-commit): '/backups/OS'
Delete subvolume (no-commit): '/backups/debian/20171019-112453'
Delete subvolume (no-commit): '/backups/debian/20171021-072305'
Delete subvolume (no-commit): '/backups/debian/20171022-085634'
Delete subvolume (no-commit): '/backups/debian/20171023-144315'
Delete subvolume (no-commit): '/backups/debian'


TODO:

snapman --subvolume-info /data/documents
Size: 1 Gib
Snapshots: 12
Sections: 2
Last /data/snapman/documents/20171011-142007 (1 hour ago)
Older /data/snapman/documents/20170409-140700 (12 days ago)

------------------------------------------------


snapman --snapshot-info /datos/snapman/movies
Subvolume: /datos/movies
Age: 2 weeks
Size: 10 Gib
Diff: -3 Gib

