# Maintainer: Manuel Domínguez López <mdomlop at gmail dot com>

_pkgver_year=2018
_pkgver_month=01
_pkgver_day=09

_name=snapman
_gitname=${_name}-git

pkgname=${_name}-local
pkgver=0.9.1b
pkgrel=1
pkgdesc="A backup system based on Btrfs snapshots."
url="https://github.com/mdomlop/${_gitname}"
source=()
md5sums=('SKIP')
license=('GPL3')
arch=('any')
depends=('python>=3.5', 'btrfs-progs')
makedepends=('pandoc')
changelog=ChangeLog
backup=('etc/snapman.ini')
install="${_name}.install"

conflicts=($_gitname)
provides=($_gitname)

build() {
    cd "$startdir"
    make
    }

package() {
    cd "$startdir"
    make arch_install DESTDIR=${pkgdir} PREFIX='/usr'
}
