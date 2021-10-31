#!/bin/sh
# file: stepviewer.sh
# vim:fileencoding=utf-8:fdm=marker:ft=sh
# Script to display STEP files using OpenCascade's DRAWEXE
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2021-10-31T02:35:43+0200
# Last modified: 2021-10-31T02:04:46+0100

export CASROOT="/usr/local/OpenCAS"
export ARCH="64"

# ----- Set envoronment variables used by OCCT -----
export CSF_LANGUAGE=us
export MMGT_CLEAR=1
export CSF_SHMessage="${CSF_OCCTResourcePath}/SHMessage"
export CSF_MDTVTexturesDirectory="${CSF_OCCTResourcePath}/Textures"
export CSF_ShadersDirectory="${CSF_OCCTResourcePath}/Shaders"
export CSF_XSMessage="${CSF_OCCTResourcePath}/XSMessage"
export CSF_TObjMessage="${CSF_OCCTResourcePath}/TObj"
export CSF_StandardDefaults="${CSF_OCCTResourcePath}/StdResource"
export CSF_PluginDefaults="${CSF_OCCTResourcePath}/StdResource"
export CSF_XCAFDefaults="${CSF_OCCTResourcePath}/StdResource"
export CSF_TObjDefaults="${CSF_OCCTResourcePath}/StdResource"
export CSF_StandardLiteDefaults="${CSF_OCCTResourcePath}/StdResource"
export CSF_IGESDefaults="${CSF_OCCTResourcePath}/XSTEPResource"
export CSF_STEPDefaults="${CSF_OCCTResourcePath}/XSTEPResource"
export CSF_XmlOcafResource="${CSF_OCCTResourcePath}/XmlOcafResource"
export CSF_MIGRATION_TYPES="${CSF_OCCTResourcePath}/StdResource/MigrationSheet.txt"

# ----- Draw Harness special stuff -----
export TCL_DIR="/usr/local/lib"
export TK_DIR="/usr/local/lib"
export FREETYPE_DIR="/usr/local/lib"
export FREEIMAGE_DIR=""
export TBB_DIR=""
export VTK_DIR="/usr/local/lib"
export FFMPEG_DIR=""
export TCL_VERSION_WITH_DOT="8.6"
export TK_VERSION_WITH_DOT="8.6"
export CSF_OCCTBinPath="bin"
export CSF_OCCTLibPath="/usr/local/lib"
export CSF_OCCTIncludePath="/usr/local/include/OpenCASCADE"
export CSF_OCCTResourcePath="/usr/local/OpenCAS/resources"
export CSF_OCCTDataPath="/usr/local/OpenCAS/data"
export CSF_OCCTSamplesPath="/usr/local/OpenCAS/samples"
export CSF_OCCTTestsPath="/usr/local/OpenCAS/tests"
export CSF_OCCTDocPath="share/doc/opencascade"

if [ -e "${CSF_OCCTResourcePath}/DrawResources" ]; then
  export DRAWHOME="${CSF_OCCTResourcePath}/DrawResources"
  export CSF_DrawPluginDefaults="${CSF_OCCTResourcePath}/DrawResources"

  if [ -e "${CSF_OCCTResourcePath}/DrawResources/DrawDefault" ]; then
    export DRAWDEFAULT="${CSF_OCCTResourcePath}/DrawResources/DrawDefault"
  fi
fi

DRAWEXE -i -c "pload ALL;vinit;stepread ${1} a *;vsetdispmode 1;vdisplay a_1;vsetmaterial aluminium;vfit;vaxo"
