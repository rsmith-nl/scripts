Miscellaneous short utilities
#############################

:date: 2015-05-14
:tags: python, shell
:author: Roland Smith

.. Last modified: 2015-05-14 22:56:07 +0200

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

Convert DICOM_ files from an x-ray machine to PNG format, remove blank areas.
The blank area removal is based on the image size of a Philips flat detector.
The image goes from 2048x2048 pixels to 1574x2048 pixels."""

.. _DICOM: http://en.wikipedia.org/wiki/DICOM


ffmutt.sh
---------

Small helper script to start mutt_ in an urxvt_ terminal for a ``mailto`` link.

.. _mutt: http://www.mutt.org/
.. _urxvt: http://software.schmorp.de/pkg/rxvt-unicode.html


find-modified.sh
----------------

Front-end for find_ to locate all files under the current directory that have
been modified up to a given number of days ago.

.. _find: https://www.freebsd.org/cgi/man.cgi?query=find


fixbb.sh
--------

Corrects the ``BoundingBox`` for single-page PostScript_ documents.

.. _PostScript: http://en.wikipedia.org/wiki/PostScript


genbackup.sh
------------

Generates a backup of the directory it is called from in the form of
a tar-file. The name of the backup file generally consists of;

* the word ``backup``,
* the date in the form YYYYMMDD,
* the short hash-tag if the directory is managed by git_.

.. _git: http://git-scm.com/

These parts are separated by dashes. The file has the extension ``tar``.

genotp.py
---------

Generates an old-fashioned one-time pad; 65 lines of 12 groups of 5 random
capital letters.

genpw.py
--------

Generates random passwords.


git-check-all.py
----------------

Find all directories in the user's home directory that are managed with git,
and run ``git gc`` on them unless they have uncommitted changes.


git-origdate.py
---------------

For all command-line arguments, print out when they were first checked into
``git``.

gitdates.py
-----------

For each file in a directory managed by git, get the short hash and data of
the most recent commit of that file.


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

