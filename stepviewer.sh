#!/bin/sh
# file: stepviewer.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
# Script to display STEP files using OpenCascade's DRAWEXE
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2021-10-31T02:35:43+0200
# Last modified: 2021-11-02T14:34:33+0100

export CASROOT="/usr/local/OpenCAS"
export CSF_OCCTResourcePath="/usr/local/OpenCAS/resources"
export DRAWHOME="${CSF_OCCTResourcePath}/DrawResources"
export CSF_DrawPluginDefaults="${CSF_OCCTResourcePath}/DrawResources"
export DRAWDEFAULT="${CSF_OCCTResourcePath}/DrawResources/DrawDefault"

DRAWEXE -i -c "pload ALL;vinit;stepread \"${1}\" a *;vsetdispmode 1;vdisplay a_1;vsetmaterial aluminium;vaxo;vfit"
