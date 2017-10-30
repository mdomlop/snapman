PREFIX='/usr'
DESTDIR=''
TEMPDIR := $(shell mktemp -u --suffix .snapman)
DOCS = README INSTALL USAGE FAQ
VERSION = 0.9a

default: man README.md

man: snapman.1.gz snapman.5.gz

snapman.1.gz: man/en/snapman.1.md
	pandoc $^ -s -t man |  gzip -c > $@

snapman.5.gz: man/en/snapman.5.md
	pandoc $^ -s -t man |  gzip -c > $@

README.md:
	cat $(DOCS) > $@

install: $(DOCS)
	install -d -m 755 $(DESTDIR)$(PREFIX)/share/doc/snapman
	install -Dm 644 $^ $(DESTDIR)$(PREFIX)/share/doc/snapman
	install -Dm 755 src/snapman.py $(DESTDIR)$(PREFIX)/bin/snapman
	install -Dm 644 src/snapman.ini $(DESTDIR)/etc/snapman.ini
	install -Dm 644 src/snapman.service $(DESTDIR)/lib/systemd/system/snapman.service
	install -d -m 755 $(DESTDIR)$(PREFIX)/share/licenses/snapman
	install -Dm 644 LICENSE $(DESTDIR)$(PREFIX)/share/licenses/snapman/COPYING
	install -Dm 644 snapman.1.gz $(DESTDIR)$(PREFIX)/share/man/man1/snapman.1.gz
	install -Dm 644 snapman.5.gz $(DESTDIR)$(PREFIX)/share/man/man5/snapman.5.gz

uninstall:
	rm -f $(PREFIX)/bin/snapman
	rm -f /etc/snapman.ini
	rm -f /lib/systemd/system/snapman.service
	rm -f $(PREFIX)/share/man/man1/snapman.1.gz
	rm -f $(PREFIX)/share/man/man5/snapman.5.gz
	rm -rf $(PREFIX)/share/licenses/snapman/
	rm -rf $(PREFIX)/share/doc/snapman/

clean:
	rm -rf *.xz *.md *.gz *.tgz *.deb /tmp/tmp.*.snapman debian/changelog debian/README debian/files debian/snapman debian/debhelper-build-stamp debian/snapman*

pkg:
	mkdir $(TEMPDIR)
	tar cf $(TEMPDIR)/snapman.tar ../snapman
	cp pacman/* ChangeLog $(TEMPDIR)/
	cd $(TEMPDIR); makepkg
	cp $(TEMPDIR)/snapman-*.pkg.tar.xz .
	@echo Package done!
	@echo You can install it as root with:
	@echo pacman -U snapman-*.pkg.tar.xz

deb:
	cp README debian/README
	cp ChangeLog debian/changelog
	#fakeroot debian/rules clean
	#fakeroot debian/rules build
	fakeroot debian/rules binary
	mv ../snapman_$(VERSION)_all.deb .
	@echo Package done!
	@echo You can install it as root with:
	@echo dpkg -i snapman_$(VERSION)_all.deb

