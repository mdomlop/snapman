PREFIX = '/usr'
DESTDIR = ''
DOCS = FAQ NEWS THANKS BUGS INFO
COMPILED_DOCS = README.md ChangeLog AUTHORS USAGE.html $(EXECUTABLE_NAME).1.html $(EXECUTABLE_NAME).5.html
PROGRAM_NAME := $(shell grep ^PROGRAM_NAME INFO | cut -d= -f2)
EXECUTABLE_NAME := $(shell grep ^EXECUTABLE_NAME INFO | cut -d= -f2)
AUTHOR := $(shell grep ^AUTHOR INFO | cut -d= -f2)
SOURCE := $(shell grep ^SOURCE INFO | cut -d= -f2)
VERSION := $(shell grep ^VERSION INFO | cut -d= -f2)
LICENSE := $(shell grep ^LICENSE INFO | cut -d= -f2)
MAIL := $(shell grep ^MAIL INFO | cut -d= -f2 | tr '[A-Za-z]' '[N-ZA-Mn-za-m]')
TIMESTAMP = $(shell LC_ALL=C date '+%a, %d %b %Y %T %z')
YEAR = 2018

PYDIR = $(shell python3 -c 'import site;print(site.getsitepackages()[0])')
MODULES = src/$(PROGRAM_NAME)/about.py src/$(PROGRAM_NAME)/functions.py src/$(PROGRAM_NAME)/program_info.py src/$(PROGRAM_NAME)/quit.py src/$(PROGRAM_NAME)/settings.py src/$(PROGRAM_NAME)/args.py src/$(PROGRAM_NAME)/gui.py src/$(PROGRAM_NAME)/section.py src/$(PROGRAM_NAME)/paths.py


dist: man docs modules

docs: $(COMPILED_DOCS) $(DOCS)

togit: clean README.md
	git add .
	git push origin

AUTHORS: authors.in
	sed s/@mail@/$(MAIL)/g $^ > $@

README.md: README USAGE INSTALL
	@echo '![@executable_name@-preview](https://github.com/mdomlop/@executable_name@/blob/master/preview.png "@executable_name@ interface")' > $@
	@echo >> $@
	cat README USAGE INSTALL >> README.md
	sed -i "s|@executable_name@|$(EXECUTABLE_NAME)|g" $@
	sed -i "s|@version@|$(VERSION)|g" $@

ChangeLog: changelog.in
	sed "s|@mail@|$(MAIL)|g" $^ > $@

version_update: purge README.md ChangeLog

man: $(EXECUTABLE_NAME).1.gz $(EXECUTABLE_NAME).5.gz

man_clean:
	rm -f $(EXECUTABLE_NAME).1.gz $(EXECUTABLE_NAME).5.gz

$(EXECUTABLE_NAME).1.gz: man/en/$(EXECUTABLE_NAME).1.md
	pandoc -s -t man $^ | gzip -c > $@

$(EXECUTABLE_NAME).5.gz: man/en/$(EXECUTABLE_NAME).5.md
	pandoc -s -t man $^ | gzip -c > $@

html: $(EXECUTABLE_NAME).1.html $(EXECUTABLE_NAME).5.html USAGE

html_clean:
	rm -f $(EXECUTABLE_NAME).1.html $(EXECUTABLE_NAME).5.html USAGE.html

$(EXECUTABLE_NAME).1.html: man/en/$(EXECUTABLE_NAME).1.md
	pandoc -s $^ > $@

$(EXECUTABLE_NAME).5.html: man/en/$(EXECUTABLE_NAME).5.md
	pandoc -s $^ > $@

USAGE.html: USAGE
	pandoc -s $^ > $@

src/$(PROGRAM_NAME)/paths.py:
	@echo 'docpath = "$(PREFIX)/share/doc/$(EXECUTABLE_NAME)"' > $@

modules: $(MODULES)

modules_clean:
	rm -f src/$(PROGRAM_NAME)/paths.py
	rm -rf src/__pycache__ src/$(PROGRAM_NAME)/__pycache__

install_executables:
	install -Dm 755 src/$(EXECUTABLE_NAME).py $(DESTDIR)$(PREFIX)/bin/$(EXECUTABLE_NAME)
	install -Dm 644 src/$(EXECUTABLE_NAME).ini $(DESTDIR)/etc/$(EXECUTABLE_NAME).ini

install_services:
	install -Dm 644 src/$(EXECUTABLE_NAME).service $(DESTDIR)/lib/systemd/system/$(EXECUTABLE_NAME).service

install_docs:
	install -dm 755 $(DESTDIR)$(PREFIX)/share/doc/$(EXECUTABLE_NAME)
	install -Dm 644 $(DOCS) $(COMPILED_DOCS) $(DESTDIR)$(PREFIX)/share/doc/$(EXECUTABLE_NAME)
	install -Dm 644 LICENSE $(DESTDIR)$(PREFIX)/share/licenses/$(EXECUTABLE_NAME)/COPYING

install_manuals:
	install -Dm 644 $(EXECUTABLE_NAME).1.gz $(DESTDIR)$(PREFIX)/share/man/man1/$(EXECUTABLE_NAME).1.gz
	install -Dm 644 $(EXECUTABLE_NAME).5.gz $(DESTDIR)$(PREFIX)/share/man/man5/$(EXECUTABLE_NAME).5.gz

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
	rm -f $(PREFIX)/share/man/man1/$(EXECUTABLE_NAME).1.gz
	rm -f $(PREFIX)/share/man/man5/$(EXECUTABLE_NAME).5.gz
	rm -rf $(PREFIX)/share/licenses/$(EXECUTABLE_NAME)/
	rm -rf $(PREFIX)/share/doc/$(EXECUTABLE_NAME)/
	rm -rf $(PYDIR)/$(PROGRAM_NAME)

clean: arch_clean debian_clean man_clean html_clean modules_clean
	rm -f ChangeLog README.md AUTHORS

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

debian_pkg: clean debian/compat debian/control debian/rules debian/changelog debian/README
	#fakeroot debian/rules clean
	#fakeroot debian/rules build
	fakeroot debian/rules binary
	mv ../$(EXECUTABLE_NAME)_$(VERSION)_all.deb .
	@echo Package done!
	@echo You can install it as root with:
	@echo dpkg -i $(EXECUTABLE_NAME)_$(VERSION)_all.deb

debian_clean:
	rm -rf debian $(EXECUTABLE_NAME)_$(VERSION)_all.deb

arch_pkg: clean ChangeLog
	sed -i "s|pkgname=.*|pkgname=$(EXECUTABLE_NAME)|" PKGBUILD
	sed -i "s|pkgver=.*|pkgver=$(VERSION)|" PKGBUILD
	makepkg
	@echo Package done!
	@echo You can install it as root with:
	@echo pacman -U $(EXECUTABLE_NAME)-$(VERSION)-1-any.pkg.tar.xz

arch_clean:
	rm -rf pkg $(EXECUTABLE_NAME)-$(VERSION)-1-any.pkg.tar.xz

