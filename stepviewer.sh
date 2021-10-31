#!/bin/sh
# file: stepviewer.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
# Script to display STEP files using OpenCascade's DRAWEXE
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2021-10-31T02:35:43+0200
# Last modified: 2021-10-31T10:43:39+0100

export CASROOT="/usr/local/OpenCAS"
export ARCH="64"
export CSF_OCCTResourcePath="/usr/local/OpenCAS/resources"
if [ -e "${CSF_OCCTResourcePath}/DrawResources" ]; then
  export DRAWHOME="${CSF_OCCTResourcePath}/DrawResources"
  export CSF_DrawPluginDefaults="${CSF_OCCTResourcePath}/DrawResources"

  if [ -e "${CSF_OCCTResourcePath}/DrawResources/DrawDefault" ]; then
    export DRAWDEFAULT="${CSF_OCCTResourcePath}/DrawResources/DrawDefault"
  fi
fi

DRAWEXE -i -c "pload ALL;vinit;stepread ${1} a *;vsetdispmode 1;vdisplay a_1;vsetmaterial aluminium;vaxo;vfit"
