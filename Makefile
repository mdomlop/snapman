PREFIX='/usr'
DESTDIR=''
TEMPDIR := $(shell mktemp -u --suffix .snapman)
DOCS = AUTHORS BUGS ChangeLog FAQ INSTALL NEWS README THANKS TODO
VERSION = 0.9a

default: man markdown

man: snapman.1.gz snapman.5.gz

snapman.1.gz: man/en/snapman.1.md
	pandoc $^ -s -t man |  gzip -c > $@

snapman.5.gz: man/en/snapman.5.md
	pandoc $^ -s -t man |  gzip -c > $@

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
	rm -rf *.xz *.md *.gz *.tgz *.deb /tmp/tmp.*.snapman

AUTHORS.md: AUTHORS
	cp $^ $@
BUGS.md: BUGS
	cp $^ $@
ChangeLog.md: ChangeLog
	cp $^ $@
FAQ.md: FAQ
	cp $^ $@
INSTALL.md: INSTALL
	cp $^ $@
NEWS.md: NEWS
	cp $^ $@
README.md: README
	cp $^ $@
THANKS.md: THANKS
	cp $^ $@
TODO.md: TODO
	cp $^ $@

markdown: AUTHORS.md BUGS.md ChangeLog.md FAQ.md INSTALL.md NEWS.md README.md THANKS.md TODO.md

pkg:
	mkdir $(TEMPDIR)
	tar cf $(TEMPDIR)/snapman.tar ../snapman
	cp packages/* ChangeLog $(TEMPDIR)/
	cd $(TEMPDIR); makepkg
	cp $(TEMPDIR)/snapman-*.pkg.tar.xz .
	@echo Package done!
	@echo You can install it as root with:
	@echo pacman -U snapman-*.pkg.tar.xz

deb: man
	checkinstall -y --install=no \
	--pkgname=snapman \
	--pkgversion=$(VERSION) \
	--pkgarch=all \
	--pkgrelease=1 \
	--pkglicense=GPLv3+ \
	--pkggroup=retrosmart \
	--pkgsource=https://github.com/mdomlop/snapman/archive/$(VERSION).tar.gz \
	--pkgaltsource=https://github.com/mdomlop/snapman/archive/$(VERSION).zip \
	--maintainer=mdomlop@gmail.com \
	--provides=snapman \
	--requires="python3 \(\>= 3.5\),btrfs-progs \(\>=4.7\)" \
	--conflicts=snapman-git \
	--nodoc
