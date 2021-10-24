Miscellaneous short utilities
#############################

:tags: python, shell
:author: Roland Smith

.. Last modified: 2021-10-24T18:46:37+0200

Introduction
============

This is a collection of small utilities that I've written over the years.
Some of them are simple front-ends for a utility with some standard options,
to save me from having to recall the options every time I need them.

Another portion are basically Python_ front-ends to run a utility in parallel
on different files.

.. _Python: http://www.python.org/

All the functions in the python scripts come with documentation strings to
explain what they do. The shell scripts have comments where necessary. They
use basic ``sh`` syntax and to not use ``bash`` extensions.

All these programs are tested and in use on the FreeBSD operating system. The
shell-scripts use the plain old ``sh`` that comes with FreeBSD, but should
work with ``bash``. Bug reports and patches welcome. Most of it should work on
other BSD systems, Linux or OS-X without major problems.
Scripts that require FreeBSD are noted as such.

All Python scripts use Python 3 specific features. Most recently I converted
``str.format`` calls to f-strings, meaning that you'll need Python 3.6 or
later for the Python scripts.


Running tests
=============

Tests for some of the functions used in the Python scripts are contained in
``scripts-tests.py``. Running the tests requires ``pytest``. Running the tests
is done as follows::

    pytest scripts-tests.py

Tests for security issues of the Python scripts can be done with ``bandit``.
I've run the tests as follows::

    bandit -s B404 -x scripts-tests.py *.py | less

One might consider adding B603 and B607 to the exclusion list when the use of
``subprocess`` calls has been audited. These are:

* B603 subprocess_without_shell_equals_true
* B607 start_process_with_partial_path

When run with::

    bandit -s B404,B603,B607 -x scripts-tests.py *.py

The file ``scripts-tests.py`` is excluded because it contains lots of
``assert`` calls as part of the testing mechanism. In this case, these are no
cause for alarm.

The result should be: ``No issues identified.``

Further general testing of Python scripts is done with ``pylama``.
The aim is to have no warnings or errors.


The programs
============


all-git.py
----------

This script traverses all the directories under the current directory.
If it finds a directory that is managed by git_, it runs ``git log`` to get
the time and hash of the latest commit.
This is then printed followed by the directory name.

.. _git: http://git-scm.com/

blocklist.py
------------

This script generates configuration data for dnsmasq_ and unbound_ to block
facebook and ad networks.

.. _dnsmasq: http://www.thekelleys.org.uk/dnsmasq/doc.html
.. _unbound: https://nlnetlabs.nl/projects/unbound/about/


clean.sh
--------

This script removes several types of generated files from the directory it is
called from.


csv2tbl.py
----------

Convert a CSV file to a LaTeX table.


default_options.py
------------------

This script generates a list of names of installed packages for which the
options on the related port are equal to the default options.


denylog.py
----------

This script reads `/var/log/security` or any other file that contains ipfw_
log messages, and makes an overview of incoming packages that have been
logged.

.. _ipfw: https://www.freebsd.org/doc/en/books/handbook/firewalls-ipfw.html

This of course requires that blocked packets are logged!

If you are writing your own firewall script, make sure to use ``deny log``
instead of just ``deny``.


dicom2jpg.py
------------

A modification of the ``dicom2png`` program mentioned below to produce JPEG
output. This is meant for situaties where lossy compression is acceptable.
For ms-windows users, this version is recommended.
Just make sure that the location where the ImageMagick programs are installed
is part of your PATH environment variable.

dicom2jpg-wand.py
+++++++++++++++++

Variant which used the wand_ binding to ImageMagick, instead of calling
``convert`` in a subprocess.
It is advised to use ImageMagick 7 with “wand”.
This is what I use myself.
For programmers, wand_ is a very Pythonic interface to ImageMagick.


dicom2png.py
------------

Convert DICOM_ files from an x-ray machine to PNG format, remove blank areas.
The blank area removal is based on the image size of a Philips flat detector.
The image goes from 2048x2048 pixels to 1574x2048 pixels.

.. _DICOM: http://en.wikipedia.org/wiki/DICOM

This program requires the `convert`` program from ImageMagick_.
For ms-windows users, this version is recommended.

Multiple images are processed in parallel using a ``ThreadPoolExecutor`` from
the ``concurrent.futures`` module to start subprocesses using as many worker
processes as your CPU has cores. This number is determined by the
``os.cpu_count`` function, so this program requires at least Python 3.4.

This version is recommended for ms-windows users.

dicom2png-wand.py
+++++++++++++++++

Variant which used the wand_ binding to ImageMagick, instead of calling
``convert`` in a subprocess.
It is advised to use ImageMagick 7 with “wand”.


dvd2webm.py
-----------

(Note that I don't use this much anymore. These days I tend to use Handbrake
for my encoding needs.)


When I buy DVDs, I generally transfer their contents to my computer for easier
viewing. However, the video and audio format used on DVD is not very compact.
So I tend to use ffmpeg_ to convert it to smaller formats without losing
quality. As of 2016, my favorite storage format is a webm_ container with
a VP9_ video stream and vorbis_ audio.

.. _VP9: https://en.wikipedia.org/wiki/VP9

Initially I used the simple ``webm.sh`` script mentioned below.
This had some shortcomings. It does not crop the video and cannot incorporate
subtitles. It does enable multiple quality setting, but I seldomly used those.

The ``dvd2webm.py`` script performs a 2-pass encoding in `constrained quality`_
mode. Optionally it also adds subtitles to the video, and starts from an
offset.

.. _constrained quality: http://wiki.webmproject.org/ffmpeg/vp9-encoding-guide


eps2png.sh
----------

This script uses ghostscript_ to render encapsulated PostScript files to PNG
format. Using command-line arguments the resolution and the type of PNG file
can be changed.

.. _ghostscript: http://www.ghostscript.com/

epubinfo
--------

Extract and print the metadata from an epub_ file, a standardized_ form of
book readable on a computer, tablet or other compatible device.

The metadata is contained in a file traditionally named ``content.opf``, which
might or might not be located in the root directory of the zip-file that is an
epub.

.. _epub: https://en.wikipedia.org/wiki/EPUB
.. _standardized: https://www.w3.org/publishing/epub32/


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


find-pkg-upgrades.py
--------------------

Script for FreeBSD to compare the versions of locally installed packages to
the versions available from the FreeBSD `package repo mirror`_. It will tell
you which packages can be upgraded via ``pkg upgrade``, and which have to be
built from source.

.. _package repo mirror: http://pkg.freebsd.org/


fixbb.sh
--------

Corrects the ``BoundingBox`` for single-page PostScript_ documents.
It requires the ghostscript_ program.

.. _PostScript: http://en.wikipedia.org/wiki/PostScript


foto4lb.py
----------

Scales fotos for including them into LaTeX documents. The standard
configuration sets the width to 886 pixels and sets the resolution to 300 dpi.
This gives an image 75 mm (about 3 in) wide.

foto4lb-wand.py
+++++++++++++++

This uses and requires the wand_ binding for ImageMagick.

.. _wand: https://docs.wand-py.org/en/0.6.7/

In my (limited) testing with Wand 0.6.7 it was *slightly* faster than using
``convert`` from Python with ``subprocess``.
It is definitely more Pythonic.


genbackup.sh
------------

Generates a backup of the directory it is called from in the form of
a tar-file. The name of the backup file generally consists of;

* the word ``backup``,
* the date in the form YYYYMMDD,
* the short hash-tag if the directory is managed by git_.


These parts are separated by dashes, and the file gets the ``.tar`` extension.
It requires the ``tar`` program. Tested with FreeBSD's tar. Should work with
GNU tar as long as you don't use the ``-x`` option; the exclude syntax is
different between BSD tar and GNU tar.


genotp.py
---------

Generates an old-fashioned one-time pad; 65 lines of 12 groups of 5 random
capital letters. Each pad has a header line containing a random identifier.
It was inspired by reading Neal Stephenson's Cryptonomicon.

It uses random numbers from the operating system via Python's ``os.urandom``
function.

A partial example::

    +++++ KWSNKYJLFF +++++
    01  WAGGB HJVHQ TTQPD LQUMD KFRFS GGCKA SVLLA WEUCS HTXNI DITNW RBZKM SEGGW
    02  GDSBB XECBL AUVLQ TUDPO DTXKW MWGAV DLRXT NRYAH HTGII YXEJJ JLNRC BIVDX
    03  JDQUJ QPAUT CUEHN RHIHT QYBGV WOVAQ MKVZQ WPRGL QJAVA RPLRS AXIII FKLEP
    04  WXYAD JNSAQ LBRXE QLCUX ZCLIE WPHSO OZBNH ZQLVN FAUEZ IDAJY VPQJN WVCAD
    05  BEYRE WORKU CPEGE JKKWZ XUVYU WSZXQ NOULH QOFDQ PREMG YJBIT GMOAM USKLV
    06  ZVATP YSRWH EEQDV LIPVQ FVYSY CIICG JKMOA RFJYE RUDJG HHJXI NNPNU VERMN
    07  WAHFD WGGGN GHIUM BCJNN CVBCK QXYGZ PEYLW XOGMT SJFQJ NWEBE BFBPJ IDHDB
    08  NPPEG HNONE YCJTG BFSFA NFYUR CMCGD XSKRO NSRBX WSDDX MEMLX BBMLC IMDJL
    09  PZNAK OCOXA PEGNL UAWQW YCVDM WBNZZ YQICH MTLBG LDQTW TQMCS KUYBN RUNXT
    ...


Testing /dev/random on FreeBSD
++++++++++++++++++++++++++++++

My *impression* is that the random data device on FreeBSD is pretty
good;

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

    > dd if=/dev/random of=rdata.bin bs=1K count=1K
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
FreeBSD random device is intended to provide cryptographically secure
pseudorandom data.

.. _manual: https://www.freebsd.org/cgi/man.cgi?query=random&sektion=4
.. _Wikipedia: http://en.wikipedia.org/?title=/dev/random
.. _other: http://www.2uo.de/myths-about-urandom/


genpw.py
--------

Generates random passwords. Like ``genotp``, It uses random numbers from the
operating system via Python's ``os.urandom`` function and converts them to
text using base64 encoding. On FreeBSD I think this is secure enough given the
previous section.

An example:

.. code-block:: console

    > python3 genpw.py -l 24 -g 4
    BU_7 7RcI jjce zAKo 83v8 RAk_


getbb.sh
--------

Determines the bounding box of PostScript files using ghostscript_.


get-tracks.py
-------------

After using lsdvd_ to see the tracks on a DVD, this script can be used to
extract the required tracks for viewing or transcoding.

It sxtracts the given tracks from a DVD using ``tccat`` from the ``transcode``
package.

.. _lsdvd: http://sourceforge.net/projects/lsdvd/


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


graph-deps.py
-------------

Used with FreeBSD's ``pkg info`` and ``dot`` from the graphviz_ port to graph
dependencies between packages.

.. _graphviz: http://www.graphviz.org/


gtk-razer.pyw
-------------

GUI program to set a Razer BlackWidow Elite or Razer Ornata Chroma to a static
color. Requires the GTK_ toolkit, PyGObject_ and pyusb_.

.. _GTK: https://www.gtk.org/
.. _PyGObject: https://pygobject.readthedocs.io/en/latest/
.. _pyusb: https://github.com/pyusb/pyusb

The user interface was built with glade_. The resulting XML file
``gtk-razer.glade`` was then compressed and ``base85`` encoded for inclusion
in the script.

.. _glade: https://glade.gnome.org/

It should work on operating systems that support pyusb_,
without requiring a kernel driver like the `openrazer driver`_ for Linux.

.. _openrazer driver: https://github.com/openrazer/openrazer

To see how this works, best look at ``set-ornata-chroma.py``, which is
a simple command-line utility to do the same thing.


histdata.py
-----------

Makes a histogram of the bytes in each input file, and calculates the entropy
in each file.


img4latex.py
------------

A program to check a PDF, PNG or JPEG file and return a suitable LaTeX figure_
environment for it.

.. _figure: http://en.wikibooks.org/wiki/LaTeX/Floats,_Figures_and_Captions#Figures

this program requires  ImageMagick_ program ``identify``.

This program also requires the ghostscript_ interpreter to determine the size
of PDF files.

As of version 1.4 it reads the text block width and height in mm from
an INI-style configuration file named ``~/.img4latexrc``.
A valid example is shown below.

.. code-block:: ini

    [size]
    width = 100
    height = 200

The image is scaled so that it fits within the text block. If a bitmapped
image does not have a defined resolution, 300 pixels/inch is assumed.


lk.py
-----

Lock down files or directories.

This makes files read-only for the owner and inaccessible for the group and
others. Then it sets the user immutable and user undeletable flag on the files.
For directories, it recursively treats the files as mentioned above. It then
sets the sets the directories to read/execute only for the owner and
inaccessible for the group and others. Then it sets the user immutable and
undeletable flag on the directories as well.

Using the -u flag unlocks the files or directories, making them writable for
the owner only.

As usual, I wrote this to automate and simplify something that I was doing on
a regular basis; safeguarding important but not often changed files.

The `os.chflags` function that is used in this script is only available on
UNIX-like operating systems. So this doesn't work on ms-windows.


make-flac.py
------------

Encodes WAV files from cdparanoia to FLAC format. Processing is done in
parallel using as many subprocesses as the machine has cores. Album
information is gathered from a text file called ``album.json``.

This file has the following format::

    {
        "title": "title of the album",
        "artist": "name of the artist",
        "year": 1985,
        "genre": "rock",
        "tracks": [
            "foo",
            "bar",
            "spam",
            "eggs"
        ]
    }


.. _cdparanoia: https://www.xiph.org/paranoia/
.. _FLAC: https://xiph.org/flac/


make-mp3.py
-----------

Works like ``make-flac.py`` but uses lame_ to encode to variable bitrate MP3
files. It uses the same ``album.json`` file as make-flac.

.. _lame: http://lame.sourceforge.net/


markphotos.py
-------------

This scripts adds a copyright notice to pictures.

.. warning:: You should edit this script and update the ``cr`` string in the
   ``processfile`` function to contain your details before using this script!

.. note:: This script requires exiftool_.

.. _exiftool: https://www.sno.phy.queensu.ca/~phil/exiftool/


mkhistory.py
------------

This script takes the ``git log --oneline`` history from the current working
directory and formats it as LaTeX text with one commit per line. This is
written to a given output file or standard output if ``-`` is used as the file
name.


mkindexpic.sh
-------------

Use ``montage`` from the ImageMagick_ suite to create an index picture of all
the files given on the command-line.

.. _ImageMagick: http://www.imagemagick.org/


mkpdf.sh
--------

Use ``convert`` from the ImageMagick_ suite to convert scanned images to PDF files.

It assumes that images are scanned at 150 PPI, and the target page is A4.


nospaces.py
-----------

Replaces whitespace in filenames with underscores.


ntpclient.py
------------

A *very simple* NTP query and time setting program. It doesn't pretend to be
extremely accurate.


offsetsrt.py
------------

Reads an SRT_ file and applies the given offset to all times in the file.
This time-shifts all subtitles.

.. _SRT: https://en.wikipedia.org/wiki/SubRip#SubRip_text_file_format


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

The result is ``open.py``. Note that it is pretty simple. and the programs
that is uses to open files are geared towards common use. So text files are
opened in an editor, while photos and most other types are opened in a viewer.
This simplicity by design. It has no options and it only opens files and
directories. I have no intention of it becoming like OS X's open or plan9's
plumb_.

.. _plumb: http://swtch.com/plan9port/man/man1/plumb.html

This utility requires the python-magic_ module.

.. _python-magic: https://pypi.python.org/pypi/python-magic

The ``filetypes`` and ``othertypes`` dictionaries in the beginning of this
script should be changed to suit your preferences.


osversion.py
------------

Prints the value __FreeBSD_version, aka OSVERSION.


param.py
--------

Script to do simple parameter substitution in files.


pdfdiff.py
----------

Uses ``pdftotext`` and ``diff`` to generate a unified diff between two PDF
files.


pdfselect.sh
------------

Select consecutive pages from a PDF document and put them in a separate
document. Requires ghostscript_.


pdfsetinfo
----------

Update the DOCINFO dictionary in a PDF file with the given values.


pdftopdf.sh
-----------

Rewrite a PDF file using ghostscript_.


povmake.sh
----------

Front-end for POV-ray_ with a limited amount of choices for picture size and
quality.

.. _POV-ray: http://www.povray.org/


py-include.py
-------------

Program to prepare files for inclusion in Python code.

After reading a file, it optionally compresses the data using ``zlib`` and
then encodes it as text using ``base85`` encoding.
It then formats the text and adds the relevant decoding and decompression
routines.

For example, the following is the ``pylama.ini`` file processed with ``python3
py-include.py -c -t pylama.ini``:

.. code-block:: python

    # pylama.ini
    data = zlib.decompress(base64.b85decode(
        'c-nQ)O;5ux3<ltPe}(U?C9PVzW)y*@a^eKs&@_eB=}hxcB^g@(JsCr2mz^T{ePTOVfh2_-rdbI'
        'sGBT8`;F~l*mC@{MPiANjL8ePCd);c`Ms!?;wzvLQNB?vPd+Rv7X3rVCX$pI|cm8xf9(^g4%8Y'
        'u5ZtYM6>^T%HuTxg1c?EgRS;NaE+^~YNh+c#bpyOOgf3!*2GA+vYqTp2-^;sq#=bbl+A8CRXGG'
        '`~8oc+RGxZPPJX~?EIp}|;(G4G1IYSC3JUvzbuFV+pq|C{h>mP(B1H_7LLR3PKyjqPO~zXE-j6'
        '>btOj$1_rw+hV=AKOC1E@{ld74-uUe{^F'
    )).decode("utf-8")



py-ver.py
---------

List or set the ``__version__`` string in all Python files given on the
command line or recursively in all directories given on the command line.


pull-git.py
-----------

Pull the current git-managed directory from another server and rebase around that.
Works in conjunction with ``serve-git``.


recentf.py
----------

Recursively finds the most recently modified files in each directory.
List the modification date/time in ISO format followed by the path.


rename.py
---------

Renames files given on the command line to <prefix><number>, keeping the
extension of the original file. Example:

.. code-block:: console

    > ls
    img_3240.jpg  img_3246.jpg  img_3252.jpg  img_3258.jpg  img_3264.jpg
    img_3271.jpg  img_3277.jpg  img_3241.jpg  img_3247.jpg  img_3253.jpg
    img_3259.jpg  img_3265.jpg  img_3272.jpg  img_3278.jpg  img_3242.jpg
    img_3248.jpg  img_3254.jpg  img_3260.jpg  img_3266.jpg  img_3273.jpg
    img_3279.jpg  img_3243.jpg  img_3249.jpg  img_3255.jpg  img_3261.jpg
    img_3267.jpg  img_3274.jpg  img_3280.jpg  img_3244.jpg  img_3250.jpg
    img_3256.jpg  img_3262.jpg  img_3269.jpg  img_3275.jpg  img_3245.jpg
    img_3251.jpg  img_3257.jpg  img_3263.jpg  img_3270.jpg  img_3276.jpg

    > rename -p holiday2014- -w 3 img_32*

    > ls
    holiday2014-001.jpg  holiday2014-009.jpg  holiday2014-017.jpg
    holiday2014-025.jpg  holiday2014-033.jpg  holiday2014-002.jpg
    holiday2014-010.jpg  holiday2014-018.jpg  holiday2014-026.jpg
    holiday2014-034.jpg  holiday2014-003.jpg  holiday2014-011.jpg
    holiday2014-019.jpg  holiday2014-027.jpg  holiday2014-035.jpg
    holiday2014-004.jpg  holiday2014-012.jpg  holiday2014-020.jpg
    holiday2014-028.jpg  holiday2014-036.jpg  holiday2014-005.jpg
    holiday2014-013.jpg  holiday2014-021.jpg  holiday2014-029.jpg
    holiday2014-037.jpg  holiday2014-006.jpg  holiday2014-014.jpg
    holiday2014-022.jpg  holiday2014-030.jpg  holiday2014-038.jpg
    holiday2014-007.jpg  holiday2014-015.jpg  holiday2014-023.jpg
    holiday2014-031.jpg  holiday2014-039.jpg  holiday2014-008.jpg
    holiday2014-016.jpg  holiday2014-024.jpg  holiday2014-032.jpg
    holiday2014-040.jpg


scripts-tests.py
----------------

This is just a collection of tests for functions from the different Python
scripts.


serve-git.sh
------------

Start a ``git daemon`` for every directory under the current working directory
that is under git_ control.
Works in conjunction with ``pull-git``.


set-ornata-chroma-rgb.py
------------------------

This changes the color or the LEDs on a Razer Ornata Chroma keyboard to
a static RGB color. It should work on operating systems that support pyusb_,
without requiring a kernel driver like the `openrazer driver`_ for Linux.


The `openrazer driver`_ served as an inspiration and source of information
about Razer's USB protocol. At first I contemplated porting this driver to
FreeBSD. But the differences between Linux and FreeBSD would make that
a complete rewrite. Not to mention that the openrazer driver contains much
more functionality than I need. Since FreeBSD comes with ``libusb``, and
supports ``pyusb`` you can pretty much control USB devices from user space
with Python. So that's what I did.


set-title.sh
------------

Set the title of the current terminal window to the hostname or to the first
argument given on the command line.


setres.sh
---------

Sets the resolution of pictures to the provided value in dots per inch.
Uses the ``mogrify`` program from the ImageMagick_ suite.


sha256.py
---------

A utility written in pure Python_ to calculate the SHA-256 checksum of files,
for systems that don't come with such a utility.


standalone.sh
-------------

Compiles a LaTeX file with the standalone documentclass to Encapsulated
PostScript format.


statusline-i3
-------------

A small Python script that replaces conky_ for me on FreeBSD with the i3_ window
manager.

.. _conky: https://github.com/brndnmtthws/conky/wiki
.. _i3: https://i3wm.org/


sync-to.sh
----------

This script was written to simplify the syncronization of data between
different computers using rsync(1).

It assumes that:

* The other host you are synchronizing to is running the rsync(1) daemon.
* That host exposes ``/home`` as the ``[home]`` module.
* You are syncronizing a directory in your $HOME to the same directory on the
  other host.


texfilehash.py
--------------

When given TeX file names, this program determines the short hash of last
``git`` commit that changed these file. When the original filename is
``<filename>.tex``, this is written to a ``<filename>.hash``. In the TeX file
you can use ``\input`` to include the hash into the document.  It is meant as
a limited alternative to the ``vc`` bundle from CTAN.


texfonts.sh
-----------

This small shell script find Opentype fonts in my TeXlive installation and
installs symbolic links to those font files in a single directory. This
directory is then scanned by fc-cache to make the fonts available to all
programs that use fontconfig.


tifftopdf.py
------------

Convert TIFF files to PDF format using the utilities ``tiffinfo`` and
``tiff2pdf`` from the libtiff package.

.. _libtiff: http://www.remotesensing.org/libtiff/


tolower.sh
----------

Changes the names of all the files that it is given on the command-line to
lower case.


unlock-excel.py
---------------

Command-line utility to unlock excel 2007+ file.


unlock-excel.pyw
----------------

GUI version of ``unlock-excel.py``, mainly for use on ms-windows.


unlock-excel-threaded.pyw
-------------------------

GUI version of ``unlock-excel.py``, using multithreading.


vid2mkv.py
----------

Convert all video files given on the command line to theora_ / vorbis_ streams
in a `matroška`_ container using ffmpeg_. As of 3452c8a it uses
a ``ThreadPoolExecutor``.

.. _theora: http://www.theora.org/
.. _vorbis: http://www.vorbis.com/
.. _matroška: http://www.matroska.org/
.. _ffmpeg: https://www.ffmpeg.org/


vid2mp4.py
----------

Analogue to ``vid2mkv.py``, but converts to `H.264`_ (using the x264_ encoder)
/ AAC_ streams in an MP4_ container.

.. _H.264: http://en.wikipedia.org/wiki/H.264/MPEG-4_AVC
.. _x264: http://www.videolan.org/developers/x264.html
.. _AAC: http://en.wikipedia.org/wiki/Advanced_Audio_Coding
.. _MP4: http://en.wikipedia.org/wiki/MPEG-4_Part_14


warn-battery.sh
---------------

Small script to give an audible warning when the battery of a laptop is low.
Specific to FreeBSD because it uses ``sysctl``.
Also requires the audio/mpg123 package.


webm.sh
-------

Convert video files to VP9_ video and Vorbis_ audio streams in a webm_
container, using a 2-pass process.

.. _webm: https://en.wikipedia.org/wiki/WebM


ytfd.py
-------

Checks youtube for the latest video's from your favorite channels.
It requires you to have a JSON-file called ``.ytfdrc`` in your
``$HOME`` directory. What this file should contain is documented in the script.


x-razer.pyw
-----------

Tkinter GUI to change the color on a Razer keyboard. Succesfulle tested on an
Ornata Chroma and a BlackWidow Elite.
