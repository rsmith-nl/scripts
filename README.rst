Miscellaneous short utilities
#############################

:date: 2015-05-14
:tags: python, shell
:author: Roland Smith

.. Last modified: 2015-05-15 16:39:28 +0200

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
It requires the ghostscript_ software.

.. _PostScript: http://en.wikipedia.org/wiki/PostScript
.. _ghostscript: http://www.ghostscript.com/


genbackup.sh
------------

Generates a backup of the directory it is called from in the form of
a tar-file. The name of the backup file generally consists of;

* the word ``backup``,
* the date in the form YYYYMMDD,
* the short hash-tag if the directory is managed by git_.

.. _git: http://git-scm.com/

These parts are separated by dashes, and the file gets the ``.tar`` extension.
It requires the ``tar`` program. Tested with FreeBSD's tar. Should work with
GNU tar as long as you don't use the ``-x`` option; the exclude syntax is
different between BSD tar and GNU tar.

genotp.py
---------

Generates an old-fashioned one-time pad; 65 lines of 12 groups of 5 random
capital letters. It was inspired by reading Neal Stephenson's Cryptonomicon.

It uses random numbers from the operating system via Python's ``os.urandom``
function.  My *impression* is that the random data device on FreeBSD is pretty
good.  Testing the ``/dev/urandom`` device on FreeBSD;

.. code-block:: console

    > ./ent -u
    ent --  Calculate entropy of file.  Call
            with ent [options] [input-file]

            Options:   -b   Treat input as a stream of bits
                    -c   Print occurrence counts
                    -f   Fold upper to lower case letters
                    -t   Terse output in CSV format
                    -u   Print this message

    By John Walker
    http://www.fourmilab.ch/
    January 28th, 2008

    > dd if=/dev/urandom of=rdata.bin bs=1K count=1K
    1024+0 records in
    1024+0 records out
    1048576 bytes transferred in 0.086200 secs (12164455 bytes/sec)

    > ./ent rdata.bin
    Entropy = 7.999857 bits per byte.

    Optimum compression would reduce the size
    of this 1048576 byte file by 0 percent.

    Chi square distribution for 1048576 samples is 208.12, and randomly
    would exceed this value 98.57 percent of the times.

    Arithmetic mean value of data bytes is 127.5057 (127.5 = random).
    Monte Carlo value for Pi is 3.137043522 (error 0.14 percent).
    Serial correlation coefficient is 0.000771 (totally uncorrelated = 0.0).

According to the manual_ page, Wikipedia_ and other_ sources I could find the
FreeBSD random device is intended to provide a cryptographically secure
pseudorandom stream.

.. _manual: https://www.freebsd.org/cgi/man.cgi?query=random&sektion=4
.. _Wikipedia: http://en.wikipedia.org/?title=/dev/random
.. _other: http://www.2uo.de/myths-about-urandom/


genpw.py
--------

Generates random passwords. Like ``genotp``, It uses random numbers from the
operating system via Python's ``os.urandom`` function. On FreeBSD I think this
is secure enough given the previous section.


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

Makes a histogram of the bytes in each input file, and calculates the entropy
in each file.


img4latex.py
------------

A program to check a PDF, PNG or JPEG file and return a suitable LaTeX figure_
environment for it.

.. _figure: http://en.wikibooks.org/wiki/LaTeX/Floats,_Figures_and_Captions#Figures


ips.sh
------

Script to start an IPython_ session in a urxvt_ terminal.

.. _IPython: http://ipython.org/


jpeg2pdf.sh
-----------

Converts a list of JPEG files to a PDF file. It uses jpeg2ps_, ps2pdf_ and
pdftk_.

.. _jpeg2ps: https://www.ctan.org/tex-archive/support/jpeg2ps
.. _ps2pdf: http://ghostscript.com/doc/current/Ps2pdf.htm
.. _pdftk: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/


make-flac.py
------------

Encodes WAV files from cdparanoia to FLAC format. Processing is done in
parallel using as many subprocesses as the machine has cores. Title and song
information is gathered from a text file called ``titles``.

This file has the following format::

      album title
      artist
      01 title of 1st song
      ..
      14 title of 14th song

.. _cdparanoia: https://www.xiph.org/paranoia/
.. _FLAC: https://xiph.org/flac/


make-mp3.py
-----------

Works like ``make-flac.py`` but uses lame_ to encode to variable bitrate MP3
files.

.. _lame: http://lame.sourceforge.net/


mkdistinfo.sh
-------------

Makes a ``distinfo`` file for a FreeBSD port. Does the same as the ``make
makesum`` port rules, but outside of the ports tree.


mkindexpic.sh
-------------

Use ``montage`` from the ImageMagick_ suite to create an index picture of all
the files given on the command-line.

.. _ImageMagick: http://www.imagemagick.org/


mkpdf.sh
--------

Uses jpeg2ps_ and epspdf_ to convert scanned images to PDF files.

.. _epspdf: http://tex.aanhet.net/epspdf/


nospaces.py
-----------

Replaces whitespace in filenames with underscores.


old.py
------

Renames a directory by prefixing the name with ``old-``, unless that directory
already exists. If the directory name starts with a period, it removes the
period and prefixes it with ``old-dot``.

open.py
-------


This Python script is a small helper to open files from the command line. It
was inspired by a OS X utility of the same name.

A lot of my interaction with the files on my computers is done through a
command-line shell, even though I use the X Window System. One of the things I
like about the ``gvim`` editor is that it forks and detach from the shell it
was started from. With other programs one usually has to explicitly add an
``&`` to the end of the command.

Then I read about the `OS X open`_ program, and I decided to write a simple
program like it in Python.

.. _OS X open: https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man1/open.1.html

The result is open.py_. Note that it is pretty simple. This is by design. It
has no options and it only opens files and directories. I have no intention of
it becoming like OS X's open or plan9's plumb_.

.. _plumb: http://swtch.com/plan9port/man/man1/plumb.html


pdfselect.sh
------------

Select consecutive pages from a PDF document and put them in a separate
document. Requires ghostscript_.


pdftopdf.sh
-----------

Rewrite a PDF file using ghostscript_.


povmake.sh
----------

Front-end for POV-ray_ with a limited amount of choices for picture size and
quality.

.. _POV-ray: http://www.povray.org/


py-ver.py
---------

List or set the ``__version__`` string in all Python files given on the
command line or recursively in all directories given on the command line.


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

Changes the names of all the files that it is given on the command-line to
lower case.


vid2mkv.py
----------



vid2mp4.py
----------



