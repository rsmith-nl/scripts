#!/usr/bin/env python
# file: genpw.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2013-12-11T23:33:07+01:00
# Last modified: 2021-05-22T18:19:09+0200
"""
Generate random passwords.

The passwords are random data from ``os.urandom`` which is encoded in a chosen
format.
"""

import argparse
import base64
import secrets
import sys

__version__ = "2021.05.22"


def main():
    """Entry point for genpw."""
    args = setup()
    encoder_choice = {
        "base64": base64.b64encode,
        "base64-urlsafe": base64.urlsafe_b64encode,
        "ascii85": base64.a85encode,
        "base85": base64.b85encode,
    }
    encoder = encoder_choice[args.encoding]
    for _ in range(args.repeat):
        pw = genpw(args.length, encoder)
        if args.groupby > 0:
            n = args.groupby
            count = len(pw) // n
            pw = " ".join([pw[k : k + n] for k in range(0, n * count, n)])
        print(pw)


def setup():
    """Process command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-l",
        "--length",
        default=64,
        type=int,
        help="# of random characters for password (default 64)",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        choices=["base64", "base64-urlsafe", "ascii85", "base85"],
        default="base64-urlsafe",
        help="encoding for password (default base64-urlsafe)",
    )
    parser.add_argument(
        "-r",
        "--repeat",
        default=1,
        type=int,
        help="number of passwords to generate (default: 1)",
    )
    parser.add_argument(
        "-g",
        "--groupby",
        default=0,
        metavar="N",
        type=int,
        help="group by N characters (default: 0; no grouping)",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    return parser.parse_args(sys.argv[1:])


def genpw(length, encoder):
    """
    Generate a random password.

    Arguments:
        length: Length of the requested password.
        encoder: function to encode the bytes data.

    Returns:
        A password string.
    """
    d = secrets.token_bytes(2*length)
    return encoder(d).decode()[:length]


if __name__ == "__main__":
    main()
