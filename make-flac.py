#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# $Date$
#
# To the extent possible under law, Roland Smith has waived all copyright and
# related or neighboring rights to make-flac.py. This work is published from
# the Netherlands. See http://creativecommons.org/publicdomain/zero/1.0/

"""Encodes music files to FLAC format. Title and song information is
gathered from a text file called titles.
"""

import os
import sys
import subprocess
from multiprocessing import cpu_count
from time import sleep
from checkfor import checkfor

def trackdata(fname='titels'):
    tracks = []
    try:
        with open(fname, 'r') as tf:
            lines = tf.readlines()
    except IOError:
        return tracks
    album = lines.pop(0)
    artist = lines.pop(0)
    for l in lines:
        words = l.split()
        if not words:
            continue
        num = int(words.pop(0))
        ifname = 'track{:02d}.cdda.wav'.format(num)
        if os.access(ifname, os.R_OK):
            ofname = 'track{:02d}.flac'.format(num)
            title = ' '.join(words)
            tracks.append((num, title, artist, album, ifname, ofname))
    return tracks

def startflac(tinfo):
    """Use the flac(1) program to convert the music file."""
    num, title, artist, album, ifname, ofname = tinfo
    args = ['flac', '-8', '-TARTIST=' + artist, '-TALBUM=' + album,
            '-TTITLE=' + title, '-TTRACKNUM={:02d}'.format(num), 
            '-o', ofname, ifname]
    with open(os.devnull, 'w') as bb:
        p = subprocess.Popen(args, stdout=bb, stderr=bb)
    print 'Start processing "{}" as {}'.format(title, ofname) 
    return (ofname, p)

def manageprocs(proclist):
    """Check a list of subprocesses for processes that have ended and
    remove them from the list.
    """
    for it in proclist:
        fn, pr = it
        result = pr.poll()
        if result != None:
            proclist.remove(it)
            if result == 0:
                print 'Finished processing', fn
            else:
                s = 'The conversion of {} exited with error code {}.'
                print s.format(fn, result)
    sleep(0.5)

def main():
    """Main program."""
    checkfor('flac')
    procs = []
    tracks = trackdata()
    if not tracks:
        print 'No tracks found.'
        sys.exit(1)
    maxprocs = cpu_count()
    for track in tracks:
        while len(procs) == maxprocs:
            manageprocs(procs)
        procs.append(startflac(track))
    while len(procs) > 0:
        manageprocs(procs)

## This is the main program ##
if __name__ == '__main__':
    main()
