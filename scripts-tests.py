# file: scripts-tests.py
# vim:fileencoding=utf-8:ft=python
#
# Author: R.F. Smith <rsmith@xs4all.nl>
# Created: 2015-04-06 13:08:02 +0200
# Last modified: 2016-06-10 20:49:02 +0200

"""
Tests for functions in python files in the scripts directory.

To run the tests use: py.test -v scripts-tests.py
"""

from genpw import roundup, genpw
from nospaces import fixname


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
    assert len(genpw(1)) == 4
    assert len(genpw(2)) == 4
    assert len(genpw(3)) == 4
    assert len(genpw(4)) == 4
    assert len(genpw(5)) == 8
    assert len(genpw(8)) == 8
    assert len(genpw(12)) == 12


def test_fixname():
    rv = fixname('dit is  een\ttest')
    assert rv == 'dit_is_een_test'
