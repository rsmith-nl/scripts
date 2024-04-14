#!/bin/sh
# file: standalone.sh
# vim:fileencoding=utf-8:ft=sh
# Compile a LaTeX standalone document
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2018-05-02T23:35:27+0200
# Last modified: 2018-05-03T00:20:21+0200

set -e
# Discard the tex extension
NAME=${1%.tex}
# Verify that it is a standalone document.
grep '\\documentclass{standalone' ${NAME}.tex || (echo "Not a standalone"; exit 1)
# Compile and convert the document
latex -interaction=nonstopmode ${NAME}.tex
dvips -q -E -j -K ${NAME}.dvi
# Clean up.
rm -f ${NAME}.dvi ${NAME}.log ${NAME}.aux
mv ${NAME}.ps ${NAME}.eps
