#!/usr/bin/env python
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2011-12-28T14:54:23+01:00
# Last modified: 2022-11-14T19:12:35+0100
#
"""Pull the current git-managed directory from another server and rebase around that."""

import argparse
import json
import logging
import os
import subprocess
import sys

__version__ = "2020.10.30"


def main():
    """Entry point for pull-git."""
    args = setup()
    srvname = getremote(args.server)
    gdir = getpulldir()
    arglist = [
        "git",
        "pull",
        "-X",
        "theirs",
        "--rebase",
        f"git://{srvname}/{gdir}",
    ]
    cmd = " ".join(arglist)
    logging.info(f'Using command: "{cmd}"')
    subprocess.run(arglist)


def setup():
    """Process command-line arguments."""
    opts = argparse.ArgumentParser(prog="open", description=__doc__)
    opts.add_argument("-v", "--version", action="version", version=__version__)
    opts.add_argument(
        "-s",
        "--server",
        default="",
        help="remote server to use (overrides ~/.pull-gitrc)",
    )
    opts.add_argument(
        "--log",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="logging level (defaults to 'warning')",
    )
    args = opts.parse_args(sys.argv[1:])
    logging.basicConfig(
        level=getattr(logging, args.log.upper(), None),
        format="%(levelname)s: %(message)s",
    )
    logging.info(f"command line arguments = {sys.argv}")
    logging.info(f"parsed arguments = {args}")
    return args


def getremote(override):
    """Get the remote server from ~/.pull-gitrc or the command line.
    Verify that the remote is reachable, or quit.

    The contents of ~/.pull-gitrc should look like this:

    {"remote": "foo.bar.home"}

    """
    if not override:
        rcpath = os.environ["HOME"] + os.sep + ".pull-gitrc"
        try:
            with open(rcpath) as rcfile:
                config = json.load(rcfile)
        except FileNotFoundError:
            logging.error("file ~/.pull-gitrc not found and no server provided.")
            sys.exit(1)
        remote = config["remote"]
        logging.info(f"using remote '{remote}' from configuration file.")
    else:
        remote = override
        logging.info(f"using remote '{remote}' from command-line.")
    rv = subprocess.run(
        ["ping", "-c", "1", remote],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if rv.returncode == 0:
        return remote
    logging.error(f"remote {remote} cannot be reached by ICMP echo request.")
    sys.exit(2)


def getpulldir():
    """Get the name of the directory we're pulling."""
    hdir = os.path.realpath(os.environ["HOME"])
    curdir = os.getcwd()
    if not curdir.startswith(hdir):
        logging.error("current directory not in user's home directory; exiting.")
        sys.exit(3)
    gdir = curdir[len(hdir) :]
    return gdir


if __name__ == "__main__":
    main()
