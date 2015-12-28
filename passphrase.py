# file: passphrase.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-12-28 12:11:31 +0100
# Last modified: 2015-12-28 14:58:57 +0100

"""Creates a passphrase by picking words from a word list, and adding filler
characters between the words."""

import re
import random

wordfile = '/usr/share/dict/opentaal-210G-basis-gekeurd'
# wordfile = '/usr/share/dict/words'
minwordlen = 4
maxwordlen = 9
count = 3
fillchars = '!@#$%&*_-+123456789'

with open(wordfile) as df:
    words = df.readlines()
rx = re.compile('/[A-Z]+$')
words = [rx.sub('', w).lower().strip() for w in words]
words = [w for w in words if minwordlen < len(w) < maxwordlen]
aantal = len(words) + 1

choices = [words[random.randint(0, aantal)] for _ in range(count)]
filler = random.sample(fillchars, count)
phrase = ''.join([k for t in zip(choices, filler) for k in t])[:-1]
print(phrase)
