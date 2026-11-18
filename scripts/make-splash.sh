#!/usr/bin/env bash
# Make the 640x480 BIOS boot menu background from the wallpaper.
# Run from anywhere with: bash scripts/make-splash.sh
# Needs ImageMagick 7 (`magick`). The result is committed, so the ISO build
# does not need ImageMagick.
set -euo pipefail
cd "$(dirname "$0")/.."

# Scale to 480 px high, keep the centre 640 px (the knight), and darken it a
# little so the menu text stays readable.
magick theme/wallpaper/knight.png \
  -resize x480 -gravity center -crop 640x480+0+0 +repage \
  -brightness-contrast -25x0 \
  -strip -define png:color-type=2 \
  theme/boot/splash.png
echo "wrote theme/boot/splash.png"
