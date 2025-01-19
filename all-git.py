#!/usr/bin/env python
# file: all-git.py
# vim:fileencoding=utf-8:ft=python
#
# Copyright © 2020 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2020-12-13T22:19:38+0100
# Last modified: 2025-01-19T12:52:00+0100
"""Report on all subdirectories that are managed by git."""

import os
import sys
import subprocess as sp
import concurrent.futures as cf


def processdir(root):
    data = sp.run(
        ["git", "-P", "log", "-n", "1", "--pretty=%h|%aI"],
        stdout=sp.PIPE,
        stderr=sp.DEVNULL,
        text=True,
        cwd=root,
    ).stdout[:-1]
    try:
        commit_id, date = data.split("|")
        return (commit_id, date, root)
    except ValueError:
        print(f"ERROR in ‘{root}’, skipping.", file=sys.stderr)
    return None


if __name__ == "__main__":
    exec = cf.ThreadPoolExecutor()
    futlist = []
    results = []
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            futlist.append(exec.submit(processdir, root))
    for f in cf.as_completed(futlist):
        rv = f.result()
        if rv:
            results.append(rv)
    # Move the most recently changed to the end of the list.
    results.sort(key=lambda x: x[1])
    sep = " | "
    for commit_id, date, path in results:
        print(f"{commit_id:9s}{sep}{date:25s}{sep}{path}")
