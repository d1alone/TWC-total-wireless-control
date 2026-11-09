#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_root"

version=$(sed -n '1s/^twc (\([^)]*\)).*/\1/p' debian/changelog)
if [ -z "$version" ]; then
    echo "Could not read the package version from debian/changelog" >&2
    exit 1
fi

output=${1:-"$project_root/twc.deb"}
case "$output" in
    /*) ;;
    *) output="$PWD/$output" ;;
esac
mkdir -p "$(dirname "$output")"

stage=$(mktemp -d "${TMPDIR:-/tmp}/twc-package.XXXXXX")
cleanup() {
    rm -rf -- "$stage"
}
trap cleanup EXIT HUP INT TERM

install -d \
    "$stage/DEBIAN" \
    "$stage/usr/bin" \
    "$stage/usr/share/applications" \
    "$stage/usr/share/doc/twc" \
    "$stage/usr/share/pixmaps"

install -m 644 twc.py "$stage/usr/bin/twc"
chmod 755 "$stage/usr/bin/twc"
install -m 644 debian/twc.desktop "$stage/usr/share/applications/twc.desktop"
install -m 644 twc.png "$stage/usr/share/pixmaps/twc.png"
install -m 644 README.md "$stage/usr/share/doc/twc/README.md"
install -m 644 LICENSE "$stage/usr/share/doc/twc/LICENSE"
install -m 644 debian/copyright "$stage/usr/share/doc/twc/copyright"
install -m 644 debian/changelog "$stage/usr/share/doc/twc/changelog.Debian"
gzip -n -9 "$stage/usr/share/doc/twc/changelog.Debian"

awk -v version="$version" '
    /^Package: twc$/ { in_package = 1 }
    in_package && NF == 0 { exit }
    in_package && /^Package:/ {
        print
        print "Version: " version
        next
    }
    in_package { print }
' debian/control > "$stage/DEBIAN/control"

find "$stage" -type d -exec chmod 755 {} +
dpkg-deb --build --root-owner-group "$stage" "$output"
printf 'Built TWC %s package: %s\n' "$version" "$output"
