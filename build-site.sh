#!/bin/sh
# Emit the published site tree into $1.
# Run by this repo's CI as a check, and for real by ~calgacus/pages, which is
# the only repo that may publish calgacus.srht.site.
#
# Copies site/ wholesale rather than naming *.html and style.css: the site has
# grown an img/ directory, and an enumerating copy drops new assets silently —
# the published page just loses its logo, with every build still green.
set -eu
out=$1
mkdir -p "$out"
cp -R site/. "$out/"
mkdir -p "$out/figures"
cp paper/figures/*.png "$out/figures/"
cp paper/main.pdf "$out/paper.pdf"
