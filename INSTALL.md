Install instructions
--------------------

You can choose between different installation methods.

### Classic method ###

- Build and install:

        $ make
        # make install

- Uninstall:

        # make uninstall

        
### Arch Linux package ###

- Build and install:

        $ make pkg
        # pacman -U snapman-*.pkg.xz

- Uninstall:
        
        # pacman -Rsc snapman

        
### Debian package ###

- Build and install:

        $ make deb
        # dpkg -i snapman_*.deb

- Uninstall:
    
        # apt purge snapman