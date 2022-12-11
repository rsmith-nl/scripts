#!/usr/bin/env python
# file: dvd2webm.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2016-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2016-02-11T19:02:34+01:00
# Last modified: 2022-12-11T12:00:37+0100
"""
Convert an mpeg stream from a DVD to a webm file, using constrained rate VP9
encoding for video and libvorbis for audio.

It uses the first video stream and the first audio stream, unless otherwise
indicated.

Optionally it can include a subtitle in the form of an SRT file in the output.
If the subtitle is a dvdsub track number, it gets overlayed on the video track
because the webm format only allows webVTT subtitle tracks.
"""

from collections import Counter
from datetime import datetime
import argparse
import logging
import math
import os
import re
import subprocess as sp
import sys

__version__ = "2022.12.11"


def main():
    """Entry point for dvd2webm.py."""
    args = setup()
    logging.info(f"processing '{args.fn}'.")
    starttime = datetime.now()
    startstr = str(starttime)[:-7]
    logging.info(f"started at {startstr}.")
    logging.info(f"using audio stream {args.audio}.")
    tc = 1
    if not args.crop and args.detect:
        logging.info("looking for cropping.")
        args.crop = findcrop(args.fn)
        width, height, _, _ = args.crop.split(":")
        if width in ["720", "704"] and height == "576":
            logging.info("standard format, no cropping necessary.")
            args.crop = None
            tc = tile_cols(width)
    else:
        width, _, _, _ = args.crop.split(":")
        tc = tile_cols(width)
    if args.crop:
        logging.info("using cropping " + args.crop)
    subtrack, srtfile = None, None
    if args.subtitle:
        try:
            subtrack = str(int(args.subtitle))
            logging.info("using subtitle track " + subtrack)
        except ValueError:
            srtfile = args.subtitle
            logging.info("using subtitle file " + srtfile)
    a1 = mkargs(
        args.fn,
        1,
        tc,
        crop=args.crop,
        start=args.start,
        subf=srtfile,
        subt=subtrack,
        atrack=args.audio,
    )
    a2 = mkargs(
        args.fn,
        2,
        tc,
        crop=args.crop,
        start=args.start,
        subf=srtfile,
        subt=subtrack,
        atrack=args.audio,
    )
    if not args.dummy:
        origbytes, newbytes = encode(a1, a2)
    else:
        logging.basicConfig(level="INFO")
        logging.info("first pass: " + " ".join(a1))
        logging.info("second pass: " + " ".join(a2))
        return
    stoptime = datetime.now()
    stopstr = str(stoptime)[:-7]
    logging.info(f"ended at {stopstr}.")
    runtime = stoptime - starttime
    runstr = str(runtime)[:-7]
    logging.info(f"total running time {runstr}.")
    encspeed = origbytes / (runtime.seconds * 1000)
    logging.info(f"average input encoding speed {encspeed:.2f} kB/s.")


def setup():
    """Process command-line arguments and configure the program."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--log",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'info')",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "-s",
        "--start",
        type=str,
        default=None,
        help="time (hh:mm:ss) at which to start encoding",
    )
    parser.add_argument("-c", "--crop", type=str, help="crop (w:h:x:y) to use")
    parser.add_argument(
        "-d", "--dummy", action="store_true", help="print commands but do not run them"
    )
    parser.add_argument(
        "-e", "--detect", action="store_true", help="detect cropping automatically"
    )
    parser.add_argument(
        "-t",
        "--subtitle",
        type=str,
        help="srt file or dvdsub track number (default: no subtitle)",
    )
    ahelp = "number of the audio track to use (default: 0; first audio track)"
    parser.add_argument("-a", "--audio", type=int, default=0, help=ahelp)
    parser.add_argument("fn", metavar="filename", help="MPEG file to process")
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"command line arguments = {sys.argv}")
    logging.debug(f"parsed arguments = {args}")
    if not check_ffmpeg():
        sys.exit(1)
    return args


def tile_cols(width):
    return math.floor(math.log2(math.ceil(float(width) / 64.0)))


def check_ffmpeg():
    """Check the minumum version requirement of ffmpeg, and that it is built with
    the needed drivers enabled."""
    args = ["ffmpeg", "-version"]
    try:
        proc = sp.run(args, text=True, stdout=sp.PIPE, stderr=sp.DEVNULL)
    except FileNotFoundError:
        logging.error("ffmpeg not found")
        return False
    verre = r"ffmpeg version (\d+)\.(\d+)(\.(\d+))? Copyright"
    major, minor, patch, *rest = re.findall(verre, proc.stdout)[0]
    logging.info(f"found ffmpeg {major}.{minor}.{patch}")
    if int(major) < 3 and int(minor) < 3:
        logging.error(f"ffmpeg 3.3 is required; found {major}.{minor}.{patch}")
        return False
    if not re.search(r"enable-libvpx", proc.stdout):
        logging.error("ffmpeg is not built with VP9 video support.")
        return False
    if not re.search(r"enable-libvorbis", proc.stdout):
        logging.error("ffmpeg is not built with Vorbis audio support.")
        return False
    return True


def findcrop(path, start="00:10:00", duration="00:00:01"):
    """
    Find the cropping of the video file.

    Arguments:
        path: location of the file to query.
        start: A string that defines where in the movie to start scanning.
            Defaults to 10 minutes from the start. Format HH:MM:SS.
        duration: A string defining how much of the movie to scan. Defaults to
            one second. Format HH:MM:SS.

    Returns:
        A string containing the cropping to use with ffmpeg.
    """
    args = [
        "ffmpeg",
        "-hide_banner",
        "-ss",
        start,  # Start at 10 minutes in.
        "-t",
        duration,  # Parse for one second.
        "-i",
        path,  # Path to the input file.
        "-vf",
        "cropdetect",  # Use the crop detect filter.
        "-an",  # Disable audio output.
        "-y",  # Overwrite output without asking.
        "-f",
        "rawvideo",  # write raw video output.
        "/dev/null",  # Write output to /dev/null
    ]
    proc = sp.run(args, universal_newlines=True, stdout=sp.DEVNULL, stderr=sp.PIPE)
    rv = Counter(re.findall(r"crop=(\d+:\d+:\d+:\d+)", proc.stderr))
    return rv.most_common(1)[0][0]


def reporttime(p, start, end):
    """
    Report the amount of time passed between start and end.

    Arguments:
        p: number of the pass.
        start: datetime.datetime instance.
        end: datetime.datetime instance.
    """
    dt = str(end - start)[:-7]
    logging.info(f"pass {p} took {dt}.")


def mkargs(
    fn, npass, tile_columns, crop=None, start=None, subf=None, subt=None, atrack=0
):
    """Create argument list for constrained quality VP9/vorbis encoding.

    Arguments:
        fn: String containing the path of the input file
        npass: Number of the pass. Must be 1 or 2.
        tile_columns: number of tile columns.
        crop: Optional string containing the cropping to use. Must be in the
            format W:H:X:Y, where W, H, X and Y are numbers.
        start: Optional string containing the start time for the conversion.
            Must be in the format HH:MM:SS, where H, M and S are digits.
        subf: Optional string containing the name of the SRT file to use.
        subt: Optional string containing the index of the dvdsub stream to use.
        atrack: Optional number of the audio track to use. Defaults to 0.

    Returns:
        A list of strings suitable for calling a subprocess.
    """
    if npass not in (1, 2):
        raise ValueError("npass must be 1 or 2")
    if crop and not re.search(r"\d+:\d+:\d+:\d+", crop):
        raise ValueError("cropping must be in the format W:H:X:Y")
    if start and not re.search(r"\d{2}:\d{2}:\d{2}", start):
        raise ValueError("starting time must be in the format HH:MM:SS")
    numthreads = str(os.cpu_count())
    basename = fn.rsplit(".", 1)[0]
    args = [
        "ffmpeg",
        "-loglevel",
        "quiet",
        "-probesize",
        "1G",
        "-analyzeduration",
        "1G",
    ]
    if start:
        args += ["-ss", start]
    args += ["-i", fn, "-passlogfile", basename]
    speed = "2"
    if npass == 1:
        logging.info(f"using {numthreads} threads")
        logging.info(f"using {tile_columns} tile columns")
        speed = "4"
    args += [
        "-c:v",
        "libvpx-vp9",
        "-row-mt",
        "1",
        "-threads",
        numthreads,
        "-pass",
        str(npass),
        "-b:v",
        "1400k",
        "-crf",
        "33",
        "-g",
        "250",
        "-speed",
        speed,
        "-tile-columns",
        str(tile_columns),
    ]
    if npass == 2:
        args += ["-auto-alt-ref", "1", "-lag-in-frames", "25"]
    args += ["-sn"]
    if npass == 1:
        args += ["-an"]
    elif npass == 2:
        args += ["-c:a", "libvorbis", "-q:a", "3"]
    args += ["-f", "webm"]
    if not subt:  # SRT file
        args += ["-map", "0:v", "-map", f"0:a:{atrack}"]
        vf = []
        if subf:
            vf = [f"subtitles={subf}"]
        if crop:
            vf.append(f"crop={crop}")
        if vf:
            args += ["-vf", ",".join(vf)]
    else:
        fc = f"[0:v][0:s:{subt}]overlay"
        if crop:
            fc += f",crop={crop}[v]"
        else:
            fc += "[v]"
        args += ["-filter_complex", fc, "-map", "[v]", "-map", f"0:a:{atrack}"]
    if npass == 1:
        outname = "/dev/null"
    else:
        outname = basename + ".webm"
    args += ["-y", outname]
    return args


def encode(args1, args2):
    """
    Run the encoding subprocesses.

    Arguments:
        args1: Commands to run the first encoding step as a subprocess.
        args2: Commands to run the second encoding step as a subprocess.

    Return values:
        A 2-tuple of the original movie size in bytes and the encoded movie size in bytes.
    """
    oidx = args2.index("-i") + 1
    origsize = os.path.getsize(args2[oidx])
    logging.info("running pass 1...")
    logging.debug("pass 1: {}".format(" ".join(args1)))
    start = datetime.utcnow()
    proc = sp.run(args1, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error(f"pass 1 returned {proc.returncode}.")
        return origsize, 0
    else:
        reporttime(1, start, end)
    logging.info("running pass 2...")
    logging.debug("pass 2: {}".format(" ".join(args2)))
    start = datetime.utcnow()
    proc = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error(f"pass 2 returned {proc.returncode}.")
    else:
        reporttime(2, start, end)
    newsize = os.path.getsize(args2[-1])
    percentage = int(100 * newsize / origsize)
    ifn, ofn = args2[oidx], args2[-1]
    logging.info(f"the size of '{ofn}' is {percentage}% of the size of '{ifn}'.")
    return origsize, newsize  # both in bytes.


if __name__ == "__main__":
    main()
