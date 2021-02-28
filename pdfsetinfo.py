#!/usr/bin/env python
# file: pdfsetinfo.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2021 R.F. Smith <rsmith@xs4all.nl>
# Created: 2021-02-28T13:49:42+0100
# Last modified: 2021-02-28T16:01:05+0100
"""Update the DOCINFO directory in a PDF file."""

from datetime import datetime as dt
import argparse
import os
import shutil
import subprocess as sp
import sys
import tempfile

__version__ = "2021.02.28"


def main():
    """Entry point for pdfsetinfo."""
    args = setup()
    # print(f"DEBUG: args = {args}")
    rv = 0
    if len([j for j in args.__dict__.values() if j is None]) > 4:
        print("Nothing to do. Exiting.")
        return 0
    with tempfile.TemporaryDirectory() as path:
        docinfo = mkdocinfo(args, path)
        # print(f"DEBUG: docinfo = {docinfo}")
        with open(docinfo) as di:
            for ln in di:
                print(ln.strip())
        try:
            cp = sp.run(
                [
                    "gs",
                    "-q",
                    "-dBATCH",
                    "-dNOPAUSE",
                    "-sDEVICE=pdfwrite",
                    f"-sOutputFile={path+os.sep}output.pdf",
                    args.file,
                    docinfo,
                ],
                stdout=sp.DEVNULL,
                stderr=sp.DEVNULL,
            )
            rv = cp.returncode
        except FileNotFoundError:
            print("ERROR: ghostscript not found.")
            rv = 1
        else:
            # print("DEBUG: copy")
            if args.output:
                shutil.copy(f"{path+os.sep}output.pdf", args.output)
            else:
                shutil.copy(f"{path+os.sep}output.pdf", args.file)
    return rv


def setup():
    """Process command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="document title",
    )
    parser.add_argument(
        "-a",
        "--author",
        type=str,
        help="name of the person that authored the document",
    )
    parser.add_argument(
        "-s",
        "--subject",
        type=str,
        help="what is the document about",
    )
    parser.add_argument(
        "-k",
        "--keywords",
        type=str,
        help="comma separated list of keywords",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="output file path (defaults to input file path)",
    )
    parser.add_argument(
        "-p",
        "--producer",
        type=str,
        default="pdfsetinfo " + __version__,
        help="producer of the modified file (defaults to pdfsetinfo)",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("file", type=str, help="input file path")
    args = parser.parse_args(sys.argv[1:])
    return args


def mkdocinfo(args, directory):
    """Create a file “pdfmarks.txt” in the given directory, with the info from args."""
    data = []
    post = "/DOCINFO pdfmark"
    if args.title:
        data.append(f"/Title ({args.title})")
    if args.author:
        data.append(f"/Author ({args.author})")
    #    elif os.name == "posix":
    #        import pwd
    #        name = pwd.getpwuid(os.getuid()).pw_gecos
    #        data.append(f"/Author ({name})")
    if args.subject:
        data.append(f"/Subject ({args.subject})")
    if args.keywords:
        data.append(f"/Keywords ({args.keywords})")
    if args.producer:
        data.append(f"/producer ({args.producer})")
    data.append(dt.strftime(dt.now().astimezone(), "/ModDate (D:%Y%m%d%H%M%S%z)"))
    data.append(post)
    data[0] = "[ " + data[0]
    rv = directory + os.sep + "pdfmarks.txt"
    with open(rv, "w") as pdfmarks:
        pdfmarks.write(os.linesep.join(data))
    return rv


if __name__ == "__main__":
    sys.exit(main())
