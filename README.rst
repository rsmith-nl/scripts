Miscellaneous short utilities
#############################

:date: 2015-05-14
:tags: python, shell
:author: Roland Smith

.. Last modified: 2015-05-14 21:08:06 +0200

Introduction
============

This is a collection of small utilities that I've written over the years.
All of them are in the public domain.

The programs
============

backup-local.sh
---------------

Backs up mount points to other mount points. This script is designed to be run
from cron as root.

.. NOTE::
    You should *not* run this script as-is!

Change the ``__mkbackup`` calls at the end of the script to reflect your
situation.


checkfor.py
-----------

This is more of a snippet of Python code. It provides a function called
``checkfor`` that detects the availability of a required program. It is
designed to be called from the main part of a script and terminates the script
if the required program is not found.


clean.sh
--------

This script removes several types of generated files from the directory it is
called from.


clock.sh
--------

Prints the time in several timezones that interest me in my locale.
You should probably change the timezone and locale to suit your preferences.


csv2tbl.py
----------

Convert a CSV file to a LaTeX table.

dicom2png.py
------------

Convert DICOM files from an x-ray machine to PNG format, remove blank areas.
The blank area removal is based on the image size of a Philips flat detector.
The image goes from 2048x2048 pixels to 1574x2048 pixels."""


ffmutt.sh
---------

find-modified.sh
----------------

fixbb.sh
--------

genbackup.sh
------------

genotp.py
---------

genpw.py
--------

git-check-all.py
----------------

git-origdate.py
---------------

gitdates.py
-----------

histdata.py
-----------

img4latex.py
------------

ips.sh
------

jpeg2pdf.sh
-----------

make-flac.py
------------

make-mp3.py
-----------

mkdistinfo.sh
-------------

mkindexpic.sh
-------------

mkpdf.sh
--------

mkphotopage.py
--------------

nospaces.py
-----------

old.py
------

open.py
-------

pdfselect.sh
------------

pdftopdf.sh
-----------

povmake.sh
----------

py-ver.py
---------

raw2pgm.sh
----------

serve-git.sh
------------

set-title.sh
------------

setres.sh
---------

sha256.py
---------

tifftopdf.py
------------

tolower.sh
----------

vid2mkv.py
----------

vid2mp4.py
----------

