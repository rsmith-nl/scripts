#!/usr/bin/env python
# file: git-repo-info.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2022 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2022-09-26T21:49:53+0200
# Last modified: 2022-09-27T23:06:25+0200
"""
Gather and print information about a git repository.

Must be called from the root of a directory tree under git control.
That is, the directory where the subdirectory “.git” resides.
"""

import subprocess as sp
import os
import sys
import logging

__version__ = "2022.09.27"


def output(args, split=False):
    """Run a program with arguments and return its standard output.

    Arguments:
        args: list of arguments for subprocess.
        split: True if the output should be split into lines.

    Returns:
        The output of the called program.
    """
    try:
        output = sp.check_output(args, text=True)
    except sp.CalledProcessError as err:
        logging.error(f"command “{' '.join(args)}” failed with code {err.returncode}.")
        sys.exit(2)
    if split:
        return output.splitlines()
    return output


logging.basicConfig(format="%(levelname)s: %(message)s")
if not os.path.isdir(".git"):
    logging.error("this directory is not managed by git.")
    sys.exit(1)

print(f"Repo: “{os.getcwd()}”")

status = output(["git", "status"])
if "working tree clean" in status:
    print("- working tree clean")
elif "untracked files present" in status:
    print("- working tree not clean (untracked files)")
elif "Changes not staged for commit" in status:
    print("- working tree not clean (unstaged changes)")
elif "Changes to be committed" in status:
    print("- working tree not clean (staged changes)")

branches = output(["git", "branch", "--no-color"], split=True)
curbranch = [b for b in branches if b.startswith("*")][0][2:]
branches = [b[2:] if b.startswith("*") else b.strip() for b in branches]
branches = [f"“{b}”" for b in branches]
if len(branches) == 1:
    print(f"- 1 branch: {branches[0]}")
elif len(branches) > 1:
    print(f"- {len(branches)} branches: {', '.join(branches)}")
    print(f"- current branch: “{curbranch}”")

remotes = output(["git", "remote"], split=True)
if len(remotes) == 1:
    print(f"- 1 remote: “{remotes[0]}”")
elif len(remotes) > 1:
    print(f"- {len(remotes)} remote: {', '.join(f'“{r}”' for r in remotes)}")

files = output(["git", "ls-files"], split=True)
print(f"- {len(files)} files under git control")

hashes = output(["git", "log", "--pretty=format:%H"], split=True)
print(f"- {len(hashes)} commits")

objsize = int(output(["du", "-s", ".git/objects/"]).split()[0])
infosize = int(output(["du", "-s", ".git/objects/info"]).split()[0])
objsize -= infosize
packsize = int(output(["du", "-s", ".git/objects/pack"]).split()[0])
packed = packsize/objsize*100
print(f"- object storage size: {objsize} KiB ({packed:.0f}% packed)")

first_commit_date = output(["git", "log", "--pretty=format:%ai", hashes[-1]])
print("- first commit:", first_commit_date)
last_commit_date = output(["git", "log", "-1", "--pretty=format:%ai"])
print("- latest commit:", last_commit_date)
