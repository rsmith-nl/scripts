#!/usr/bin/env python
# file: scripts-tests.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2018 R.F. Smith <rsmith@xs4all.nl>.
# SPDX-License-Identifier: MIT
# Created: 2015-04-06T13:08:02+0200
# Last modified: 2019-07-27T15:11:11+0200
"""
Tests for functions in python files in the scripts directory.

To run the tests use: py.test -v scripts-tests.py
"""

from collections import Counter

from genotp import rndcaps, otp
from genpw import roundup, genpw
from nospaces import fixname
from offsetsrt import str2ms, ms2str


def test_rndcaps():
    rv = rndcaps(20)
    assert len(rv) == 20
    assert all(j in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for j in rv)
    v = Counter(rndcaps(100000)).values()
    mxc = max(v)
    mnc = min(v)
    assert mxc / mnc < 1.3


def test_otp():
    lines = otp(5).splitlines()
    assert len(lines) == 5
    for ln in lines:
        assert len(ln) == 75


def test_roundup():
    assert roundup(1) == 3
    assert roundup(2) == 3
    assert roundup(3) == 3
    assert roundup(4) == 3
    assert roundup(5) == 6
    assert roundup(6) == 6
    assert roundup(7) == 6
    assert roundup(8) == 6
    assert roundup(9) == 9


def test_genpw():
    for n in range(12):
        assert len(genpw(n)) == n


def test_fixname():
    rv = fixname("dit is  een\ttest")
    assert rv == "dit_is_een_test"


def test_srt():
    for j in range(7200):
        p = j * 10
        ts = ms2str(p)
        k = str2ms(ts)
        assert p == k
