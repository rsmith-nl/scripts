#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Make a webpage for all pictures in the current directory.
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to mkphotopage. This work is published from the
# Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

import datetime
import glob
#import zlib
#import base64

rootdir = "../../.."
today = datetime.date.today()
outfile = open('index.html', 'w')

header = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <meta http-equiv="Content-Type"
      content="text/html; charset=utf-8" />
    <meta name="generator" content="emacs" />
    <meta name="author" content="R.F. Smith" />
    <meta name="copyright" content="© {} R.F. Smith" />
    <meta name="date" content="{}" />
    <meta name="keywords" content="Roland Smith, photos" />
    <meta name="MSSmartTagsPreventParsing" content="TRUE" />
    <title>Roland's picture pages</title>
    <link rel="stylesheet" href="{}/default.css" />
  </head>
  <body>

    <!-- Koptekst. -->
    <table width="100%">
      <tbody>
        <tr>
          <td rowspan="1" colspan="1">
            <h1 class="big">Roland's picture pages</h1>
            <p>subtitle</p>
          </td>
          <td rowspan="1" colspan="1">
            <img src="{}/pics/face.jpg" alt="My picture."
                width="105" height="141" />
          </td>
        </tr>
      </tbody>
      </table><br />

      <!-- de echte tekst van de pagina begint hier. -->

      <!-- Creative Commons License -->
      <a rel="license"
         href="http://creativecommons.org/licenses/by/3.0/"><img alt="Creative
         Commons License" border="0"
         src="http://creativecommons.org/images/public/somerights20.png"
         title="Creative Commons Attribution License"
         /></a><br /> These photos are licensed under the <a rel="license"
         href="http://creativecommons.org/licenses/by/3.0/">Creative Commons
      Attribution 3.0 License</a>.
      <!-- /Creative Commons License -->

    <p>The photos on this page have been taken during ...</p>

    <table width="100%" cellpadding="10%">
      <tbody>"""

outfile.write(header.format(today.year, today, rootdir, rootdir))

flist = glob.glob("*.jpg")
flist.sort()
twinned = [(flist[i], flist[i+1]) for i in range(0, len(flist)/2*2, 2)]
picline = """        <tr valign="bottom"> <!-- Begin of row of pictures  -->
          <td align="center" width="50%">
              <img border="0" width="100%"
               src="{}" alt="{}" />
          </td>
          <td align="center" width="50%">
              <img border="0" width="100%"
               src="{}" alt="{}" />
          </td>
        </tr> <!-- End of row of pictures  -->\n"""
cmtline = """        <tr valign="top"> <!-- Begin of row of comments -->
          <td width="50%">
            {}
          </td>
          <td width="50%">
            {}
          </td>
        </tr> <!-- End of row of comments -->\n"""

for p in twinned:
    outfile.write(picline.format(p[0], p[0], p[1], p[1]))
    outfile.write(cmtline.format(p[0], p[1]))

if len(flist) % 2 == 1:
    picline = """        <tr valign="bottom"> <!-- Begin of row of pictures -->
          <td align="center" width="50%">
              <img border="0" width="100%"
               src="{}" alt="{}" />
          </td>
        </tr> <!-- End of row of pictures  -->\n"""
    cmtline = """        <tr valign="top"> <!-- Begin of row of comments -->
          <td width="50%">
            {}
          </td>
        </tr> <!-- End of row of comments -->\n"""
    outfile.write(picline.format(flist[-1], flist[-1]))
    outfile.write(cmtline.format(flist[-1]))

htmlfooter = """      </tbody>
    </table>

    <!-- einde van de pagina. Begin van de voettekst -->
    <hr />
    <p class="footer">
        Copyright &copy; {} R.F. Smith &lt;rsmith@xs4all.nl&gt;<br />
        Some pictures have been adapted/made with the
        <a href="http://www.gimp.org">GIMP</a> (GNU Image Manipulation
        Program).<br />
        <a href="http://www.gimp.org/" title="GIMP">
          <img src= "{}/pics/gfx_by_gimp.png" border="0" width="90"
           height="36" alt="GIMP" />
        </a>
        <a href="http://www.gnu.org/software/emacs/emacs.html" title="Emacs">
          <img src="{}/pics/emacs.png" border="0" width="88" height="33"
          alt="Emacs" />
        </a>
      <br />Last update: {}</p>
  </body>
</html>"""
outfile.write(htmlfooter.format(today.year, rootdir, rootdir, today))

# This footer is somewhat mangled, otherwise Emacs will pick it up.
emacsfooter = """<!-- {} -->
<!-- mode: nxml -->
<!-- time-stamp-start: "[\\">]Last update:[ \\t]+" -->
<!-- time-stamp-end: "[<\\"]" -->
<!-- time-stamp-format: "%:y-%02m-%02d %02H:%02M %Z" -->
<!-- time-stamp-line-limit: 0 -->
<!-- time-stamp-count: 2 -->
<!-- End: -->"""
outfile.write(emacsfooter.format("Local Variables:"))
outfile.close()
