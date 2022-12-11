#!/usr/bin/env python
# file: vid2webm.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2018-12-16T22:45:15+0100
# Last modified: 2022-12-11T23:09:58+0100
"""
Convert videos to webm files, using 2-pass constrained rate VP9
encoding for video and libvorbis for audio.
"""

from datetime import datetime
import argparse
import logging
import math
import os
import re
import subprocess as sp
import sys

__version__ = "2022.12.11"


def main(argv):
    """Entry point for vid2webm.py."""
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
    parser.add_argument(
        "-d", "--dummy", action="store_true", help="print commands but do not run them"
    )
    parser.add_argument(
        "files", metavar="files", nargs="+", help="one or more files to process"
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.debug(f"command line arguments = {argv}")
    logging.debug(f"parsed arguments = {args}")
    if not check_ffmpeg():
        return 1
    for fn in args.files:
        logging.info(f"processing '{fn}'.")
        starttime = datetime.now()
        startstr = str(starttime)[:-7]
        tc = get_tc(fn)
        logging.info(f"started at {startstr}.")
        a1 = mkargs(
            fn,
            1,
            tc,
            start=args.start,
        )
        a2 = mkargs(
            fn,
            2,
            tc,
            start=args.start,
        )
        if not args.dummy:
            origbytes, newbytes = encode(a1, a2)
        else:
            logging.basicConfig(level="INFO")
            logging.info("first pass: " + " ".join(a1))
            logging.info("second pass: " + " ".join(a2))
            continue
        stoptime = datetime.now()
        stopstr = str(stoptime)[:-7]
        logging.info(f"ended at {stopstr}.")
        runtime = stoptime - starttime
        runstr = str(runtime)[:-7]
        logging.info(f"total running time {runstr}.")
        encspeed = origbytes / (runtime.seconds * 1000)
        logging.info(f"average input encoding speed {encspeed:.2f} kB/s.")


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


def reporttime(p, dt):
    """
    Report the amount of time passed between start and end.

    Arguments:
        p: number of the pass.
        dt: datetime.timedelta instance.
    """
    s = str(dt)[:-7]
    logging.info(f"pass {p} took {s}.")


def get_tc(name):
    """Determine the amount of tile columns to use."""
    args = ["ffprobe", "-hide_banner", "-select_streams", "v", "-show_streams", name]
    proc = sp.run(args, text=True, stdout=sp.PIPE, stderr=sp.DEVNULL)
    lines = proc.stdout.splitlines()
    d = {}
    for ln in lines:
        if '=' in ln:
            key, value = ln.strip().split("=")
            d[key] = value
    width = d["width"]
    return math.floor(math.log2(math.ceil(float(width) / 64.0)))


def mkargs(fn, npass, tile_columns, start=None):
    """Create argument list for constrained quality VP9/vorbis encoding.

    Arguments:
        fn: String containing the path of the input file
        npass: Number of the pass. Must be 1 or 2.
        start: Optional string containing the start time for the conversion.
            Must be in the format HH:MM:SS, where H, M and S are digits.

    Returns:
        A list of strings suitable for calling a subprocess.
    """
    if npass not in (1, 2):
        raise ValueError("npass must be 1 or 2")
    if start and not re.search(r"\d{2}:\d{2}:\d{2}", start):
        raise ValueError("starting time must be in the format HH:MM:SS")
    numthreads = str(os.cpu_count())
    basename, ext = fn.rsplit(".", 1)
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
    args += ["-f", "webm", "-map", "0:v", "-map", "0:a"]
    if npass == 1:
        outname = "/dev/null"
    else:
        if ext.lower() == "webm":
            outname = basename + "_mod.webm"
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
        dt = end - start
        reporttime(1, dt)
    logging.info("running pass 2...")
    logging.debug("pass 2: {}".format(" ".join(args2)))
    start = datetime.utcnow()
    proc = sp.run(args2, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    end = datetime.utcnow()
    if proc.returncode:
        logging.error(f"pass 2 returned {proc.returncode}.")
    else:
        dt = end - start
        reporttime(2, dt)
    newsize = os.path.getsize(args2[-1])
    percentage = int(100 * newsize / origsize)
    ifn, ofn = args2[oidx], args2[-1]
    logging.info(f"the size of '{ofn}' is {percentage}% of the size of '{ifn}'.")
    return origsize, newsize  # both in bytes.


if __name__ == "__main__":
    main(sys.argv[1:])
