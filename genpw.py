#!/usr/bin/env python
# file: genpw.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2013-2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2013-12-11T23:33:07+01:00
# Last modified: 2022-01-16T14:36:27+0100
"""
Generate random passwords.

The passwords are random data from ``secrets.token_bytes`` which is encoded in a chosen
format.
"""

import argparse
import base64
import secrets
import sys
import math
import logging

__version__ = "2022.01.16"


def shannon(n):
    """
    Calculate the Shannon entropy of an alphabet of size n, where every
    character has the same chance of being selected.
    """
    return -(1/n)*math.log(1/n, 2)*n


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


parser = argparse.ArgumentParser(description=__doc__)
edef = 70
parser.add_argument(
    "--log",
    default="warning",
    choices=["debug", "info", "warning", "error"],
    help="logging level (default: warning)",
)
# The idea of using entropy is based on
# https://pthree.org/2017/09/04/a-practical-and-secure-password-and-passphrase-generator/
parser.add_argument(
    "-e",
    "--entropy",
    default=edef,
    type=int,
    help=f"bits of entropy of password (default {edef})",
)
cdef = "base85"
parser.add_argument(
    "-c",
    "--encoding",
    choices=["base64", "base64-urlsafe", "ascii85", "base85"],
    default=cdef,
    help=f"encoding for password (default {cdef})",
)
rdef = 1
parser.add_argument(
    "-r",
    "--repeat",
    default=rdef,
    type=int,
    help=f"number of passwords to generate (default: {rdef})",
)
gdef = 0
parser.add_argument(
    "-g",
    "--groupby",
    default=gdef,
    metavar="N",
    type=int,
    help=f"group by N characters (default: {gdef}, 0 = no grouping)",
)
parser.add_argument("-v", "--version", action="version", version=__version__)
args = parser.parse_args(sys.argv[1:])
logging.basicConfig(
    level=getattr(logging, args.log.upper(), None), format="%(levelname)s: %(message)s"
)

encoder_choice = {
    "base64": (base64.b64encode, 64),
    "base64-urlsafe": (base64.urlsafe_b64encode, 64),
    "base85": (base64.b85encode, 85),
}
encoder, alphabetsize = encoder_choice[args.encoding]
se = shannon(alphabetsize)
logging.info(f"{args.encoding} encoder is used, {se:.3f} bits/character entropy")
length = math.ceil(args.entropy/se)
logging.info(f"{length} characters required for ≥{args.entropy} bits of entropy")
if args.groupby:
    logging.info(f"grouping by {args.groupby} characters")
for _ in range(args.repeat):
    pw = genpw(length, encoder)
    if args.groupby > 0:
        n = args.groupby
        count = math.ceil(len(pw) / n)
        pw = " ".join([pw[k : k + n] for k in range(0, n * count, n)])
    print(pw)
