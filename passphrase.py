# file: passphrase.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-12-28 12:11:31 +0100
# Last modified: 2018-02-28 09:28:44 +0100
"""
Creates a passphrase.

It picks words from a word list, and adds filler characters between the words.
"""

import argparse
import logging
import secrets
import re
import sys

__version__ = '1.0.0'

wordfile = '/usr/share/dict/opentaal-210G-basis-gekeurd'
#wordfile = '/usr/share/dict/words'
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
    '-w',
    '--words',
    type=str,
    default=wordfile,
    help='path to words file (default: {})'.format(wordfile)
)
parser.add_argument('-c', '--count', type=int, default=4, help='number of words (default: 4)')
parser.add_argument('-v', '--version', action='version', version=__version__)
args = parser.parse_args(sys.argv[1:])
logging.basicConfig(
    level=getattr(logging, args.log.upper(), None), format='%(levelname)s: %(message)s'
)

logging.info('reading words database {}'.format(args.words))
with open(args.words) as df:
    words = df.readlines()
rx = re.compile('/[A-Z]+$')
words = [rx.sub('', w).lower().strip() for w in words]
logging.info('{} total words in {}'.format(len(words), args.words))
words = [w for w in words if minwordlen < len(w) < maxwordlen]
logging.info('{} words of correct length in {}'.format(len(words), args.words))
aantal = len(words) + 1
choices = [secrets.choice(words) for _ in range(args.count)]
filler = [secrets.choice(fillchars) for _ in range(args.count)]
phrase = ''.join([k for t in zip(choices, filler) for k in t])[:-1]
print(phrase)
