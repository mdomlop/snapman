# Maintainer: Manuel Domínguez López <mdomlop at gmail dot com>

_pkgver_year=2018
_pkgver_month=08
_pkgver_day=16

pkgname=snapman
pkgver=1.0a
pkgrel=1
pkgdesc='A backup system based on Btrfs snapshots.'
url='https://github.com/mdomlop/snapman'
source=()
license=('GPL3')
arch=('any')
depends=('btrfs-progs' 'python>=3.5' 'python-pyqt5')
makedepends=('python-docutils')
changelog=ChangeLog
backup=('etc/snapman.ini')
install="$pkgname.install"

build() {
    cd "$startdir"
    make
    }

package() {
    cd "$startdir"
    make arch_install DESTDIR="$pkgdir"
}
