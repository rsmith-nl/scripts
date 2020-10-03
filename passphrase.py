#!/usr/bin/env python3
# file: passphrase.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-12-28 12:11:31 +0100
# Last modified: 2020-10-03T07:29:10+0200
"""
Creates a passphrase.

It picks words from a word list, and adds filler characters between the words.
"""

import argparse
import logging
import secrets
import re
import sys

__version__ = "2019-08-13"

wordfiles = {
    'en': '/usr/share/dict/words',
    'nl': '/usr/share/dict/opentaal-210G-basis-gekeurd'
}
minwordlen = 4
maxwordlen = 9
fillchars = '!@#$%&*_-'

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '--log',
    default='warning',
    choices=['debug', 'info', 'warning', 'error'],
    help='logging level (default: warning)'
)
parser.add_argument(
    '-l', '--language', type=str, default='en', help='word file language (default: en)'
)
parser.add_argument(
    '-c',
    '--count',
    type=int,
    default=1,
    help='number of passphrases to generate (default: 1)'
)
parser.add_argument(
    '-w', '--words', type=int, default=3, help='number of words (default: 3)'
)
parser.add_argument('-v', '--version', action='version', version=__version__)
args = parser.parse_args(sys.argv[1:])
logging.basicConfig(
    level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
)
wf = wordfiles[args.language]
logging.info('reading words database {}'.format(wf))
with open(wf) as df:
    words = df.readlines()
rx = re.compile('/[A-Z]+$')
words = [rx.sub('', w).lower().strip() for w in words]
logging.info('{} total words in {}'.format(len(words), wf))
words = [w for w in words if minwordlen < len(w) < maxwordlen]
logging.info('{} words of correct length in {}'.format(len(words), wf))
aantal = len(words) + 1
for n in range(args.count):
    choices = [secrets.choice(words) for _ in range(args.words)]
    filler = [secrets.choice(fillchars) for _ in range(args.words)]
    phrase = ''.join([k for t in zip(choices, filler) for k in t])[:-1]
    print(phrase)
