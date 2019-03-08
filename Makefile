PREFIX = '/usr'
DESTDIR = ''
COMMIT = ''
DOCS = FAQ NEWS THANKS BUGS INFO ChangeLog README.md AUTHORS
MAN = $(patsubst %.rst,%.gz,$(wildcard man/*/*.rst))
HTML = $(patsubst %.rst,%.html,$(wildcard man/*/*.rst)) README.html

PYDIR = $(shell python3 -c 'import site;print(site.getsitepackages()[0])')
MODULES = $(wildcard src/$(PROGRAM_NAME)/*.py)

PROGRAM_NAME := $(shell grep ^PROGRAM_NAME INFO | cut -d= -f2)
EXECUTABLE_NAME := $(shell grep ^EXECUTABLE_NAME INFO | cut -d= -f2)
VERSION := $(shell grep ^VERSION INFO | cut -d= -f2)
MAIL := $(shell grep ^MAIL INFO | cut -d= -f2 | tr '[A-Za-z]' '[N-ZA-Mn-za-m]')

DEBIANPKG = $(EXECUTABLE_NAME)_$(VERSION)_all.deb
ARCHPKG = $(EXECUTABLE_NAME)-$(VERSION)-1-any.pkg.tar.xz

dist: man docs 

docs: $(HTML) $(DOCS)

man: $(MAN)
%.gz: %.rst
	rst2man $^ | gzip -c > $@
man_clean:
	rm -f $(MAN)

html: $(HTML)
%.html: %.rst
	rst2html $^ > $@
README.html: README.md
	rst2html $^ > $@
html_clean:
	rm -f $(HTML)

install_executables:
	install -Dm 755 src/$(EXECUTABLE_NAME).py $(DESTDIR)$(PREFIX)/bin/$(EXECUTABLE_NAME)
	install -Dm 644 src/$(EXECUTABLE_NAME).ini $(DESTDIR)/etc/$(EXECUTABLE_NAME).ini

install_services:
	install -Dm 644 src/$(EXECUTABLE_NAME).service $(DESTDIR)/lib/systemd/system/$(EXECUTABLE_NAME).service

install_docs:
	install -dm 755 $(DESTDIR)$(PREFIX)/share/doc/$(EXECUTABLE_NAME)
	install -Dm 644 $(DOCS) $(HTML) $(DESTDIR)$(PREFIX)/share/doc/$(EXECUTABLE_NAME)
	install -Dm 644 LICENSE $(DESTDIR)$(PREFIX)/share/licenses/$(EXECUTABLE_NAME)/COPYING

install_manuals:
	install -Dm 644 man/en/$(EXECUTABLE_NAME).1.gz $(DESTDIR)$(PREFIX)/share/man/man1/$(EXECUTABLE_NAME).1.gz
	install -Dm 644 man/en/$(EXECUTABLE_NAME).5.gz $(DESTDIR)$(PREFIX)/share/man/man5/$(EXECUTABLE_NAME).5.gz

install_graphics:
	install -Dm 644 resources/$(EXECUTABLE_NAME).svg $(DESTDIR)/$(PREFIX)/share/pixmaps/$(EXECUTABLE_NAME).svg
	install -Dm 755 resources/$(EXECUTABLE_NAME).desktop $(DESTDIR)/$(PREFIX)/share/applications/$(EXECUTABLE_NAME).desktop

install_modules: $(MODULES)
	install -m 755 -d $(DESTDIR)$(PYDIR)/$(PROGRAM_NAME)
	install -m 644 $^ $(DESTDIR)$(PYDIR)/$(PROGRAM_NAME)

install: install_executables install_docs install_manuals install_graphics install_services install_modules

arch_install_services:
	install -Dm644 src/$(EXECUTABLE_NAME).service $(DESTDIR)$(PREFIX)/lib/systemd/system/$(EXECUTABLE_NAME).service

arch_install: install_executables install_docs install_manuals install_graphics arch_install_services install_modules

uninstall:
	rm -f $(PREFIX)/bin/$(EXECUTABLE_NAME)
	rm -f $(PREFIX)/share/pixmaps/$(EXECUTABLE_NAME).svg
	rm -f $(PREFIX)/share/applications/$(EXECUTABLE_NAME).desktop
	rm -f /etc/$(EXECUTABLE_NAME).ini
	rm -f /lib/systemd/system/$(EXECUTABLE_NAME).service
	rm -f $(PREFIX)/share/man/man1/$(EXECUTABLE_NAME).?.gz
	rm -rf $(PREFIX)/share/licenses/$(EXECUTABLE_NAME)/
	rm -rf $(PREFIX)/share/doc/$(EXECUTABLE_NAME)/
	rm -rf $(PYDIR)/$(PROGRAM_NAME)

clean: arch_clean debian_clean man_clean html_clean
	rm -rf src/__pycache__ src/$(PROGRAM_NAME)/__pycache__

debian:
	mkdir debian

debian/compat: compat debian
	cp compat $@

debian/rules: rules debian
	cp rules $@

debian/changelog: ChangeLog debian
	cp ChangeLog $@

debian/control: control debian
	sed s/@mail@/$(MAIL)/g control > $@

debian/README: README.md debian
	cp README.md debian/README

debian/copyright: copyright debian
	@echo Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/ > $@
	@echo Upstream-Name: $(EXECUTABLE_NAME) >> $@
	@echo "Upstream-Contact: $(AUTHOR) <$(MAIL)>" >> $@
	@echo Source: $(SOURCE) >> $@
	@echo License: $(LICENSE) >> $@
	@echo >> $@
	sed s/@mail@/$(MAIL)/g copyright >> $@

debian_pkg: $(DEBIANPKG)
$(DEBIANPKG): debian/compat debian/control debian/rules debian/changelog debian/README
	#fakeroot debian/rules clean
	#fakeroot debian/rules build
	fakeroot debian/rules binary
	mv ../$@ .
	@echo Package done!
	@echo You can install it as root with:
	@echo dpkg -i $@


debian_clean:
	rm -rf debian $(DEBIANPKG)

arch_pkg: $(ARCHPKG)
$(ARCHPKG): PKGBUILD ChangeLog
	sed -i "s|pkgname=.*|pkgname=$(EXECUTABLE_NAME)|" PKGBUILD
	sed -i "s|pkgver=.*|pkgver=$(VERSION)|" PKGBUILD
	makepkg -d
	@echo Package done!
	@echo You can install it as root with:
	@echo pacman -U $@

arch_clean:
	rm -rf pkg $(ARCHPKG)

.PHONY: clean arch_pkg arch_clean debian_pkg debian_clean
