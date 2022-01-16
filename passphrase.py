#!/usr/bin/env python
# file: passphrase.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-12-28 12:11:31 +0100
# Last modified: 2022-01-16T13:11:39+0100
"""
Creates a passphrase.

It picks words from a word list, and adds filler characters between the words.
The generated passwords have a minimum entropy.
"""

import argparse
import logging
import math
import secrets
import itertools as it
import re
import sys

__version__ = "2022.01.16"

# Change the location of the word files to suit your situation.
wordfiles = {
    "en": "/usr/share/dict/words",
    "nl": "/usr/share/dict/opentaal-210G-basis-gekeurd",
}
minwordlen = 4
maxwordlen = 9
fillchars = "?!@#$%&*_+-,;:><[]{}"
fill_entropy = math.log(len(fillchars), 2)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--log",
    default="warning",
    choices=["debug", "info", "warning", "error"],
    help="logging level (default: warning)",
)
parser.add_argument(
    "-l", "--language", type=str, default="en", help="word file language (default: en)"
)
parser.add_argument(
    "-c",
    "--count",
    type=int,
    default=1,
    help="number of passphrases to generate (default: 1)",
)
# The idea of using entropy is based on
# https://pthree.org/2017/09/04/a-practical-and-secure-password-and-passphrase-generator/
parser.add_argument(
    "-e", "--entropy", type=int, default=70, help="bits of entropy (default: 75)"
)
parser.add_argument("-v", "--version", action="version", version=__version__)
args = parser.parse_args(sys.argv[1:])
logging.basicConfig(
    level=getattr(logging, args.log.upper(), None), format="%(levelname)s: %(message)s"
)
wf = wordfiles[args.language]
logging.info(f"reading words database {wf}")
with open(wf) as df:
    words = df.readlines()
rx = re.compile("/[A-Z]+$")
words = [rx.sub("", w).lower().strip() for w in words]
logging.info(f"{len(words)} total words in {wf}")
words = [w for w in words if minwordlen < len(w) < maxwordlen]
logging.info(f"{len(words)} words of correct length in {wf}")
word_entropy = math.log(len(words), 2)
logging.info(f"word entropy is {word_entropy:.4f} bits/word")
logging.info(f"filler entropy is {fill_entropy:.4f} bits/character")
# num_words * word_entropy + (num_words - 1) * fill_entropy ≥ args.entropy
num_words = math.ceil((args.entropy + fill_entropy) / (word_entropy + fill_entropy))
logging.info(f"{num_words} words required for ≥{args.entropy} bits of entropy")
for n in range(args.count):
    choices = [secrets.choice(words) for _ in range(num_words)]
    filler = list(secrets.choice(list(it.combinations(fillchars, num_words))))
    # Ensure that one filler character is a nonzero digit.
    filler[secrets.randbelow(num_words - 1)] = secrets.choice("123456789")
    phrase = "".join([k for t in zip(choices, filler) for k in t])[:-1]
    print(phrase)
