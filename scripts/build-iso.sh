#!/usr/bin/env bash
# Build the Cathedral ISO with mkarchiso into out/.
#
# Runs as root on an Arch system with archiso installed. Normally it runs on a
# GitHub runner inside the archlinux container that scripts/ci.sh starts, so
# packages come from the official Arch repos only.
#
# The profile is assembled in a scratch directory from separate pieces so a
# swap is a small edit:
#   profile/            releng with Cathedral's branding
#   packages/*.x86_64   package lists, joined into packages.x86_64
#   theme/              wallpaper and boot splash
set -euo pipefail
cd "$(dirname "$0")/.."

build="${BUILD_DIR:-/tmp/cathedral-build}"
rm -rf -- "$build"
mkdir -p -- "$build"

echo "› assembling the profile in $build/profile"
cp -a profile "$build/profile"
cat packages/*.x86_64 >"$build/profile/packages.x86_64"
install -Dm644 theme/boot/splash.png "$build/profile/syslinux/splash.png"
install -Dm644 theme/wallpaper/knight.png "$build/profile/airootfs/usr/share/backgrounds/cathedral/knight.png"

echo "› building with mkarchiso"
mkdir -p out
mkarchiso -v -r -w "$build/work" -o out "$build/profile"

ls -la out
