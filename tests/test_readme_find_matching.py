#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import io
import unittest
from cabinetsorter.app import Readme

class ReadmeReadFindMatchingTests(unittest.TestCase):
    """
    Testing finding matching entries in README files
    """

    def setUp(self):
        """
        Initialize some vars we'll need on every test.
        """
        self.readme = Readme(0)
        self.df = io.StringIO()

    def set_df_contents(self, lines):
        """
        Sets the contents of the "file" that we're gonna read in.
        """
        for line in lines:
            print(line, file=self.df)
        self.df.seek(0)

    def read(self, lines):
        """
        Read in our file.  Note that the `is_markdown` flag is
        currently not actually used, so we're not bothering to
        test for it at all.
        """
        self.set_df_contents(lines)
        self.readme.read_file_obj(self.df, False)

    def test_single_mod_overview(self):
        self.read([
            'Beginning Text',
            '# Overview',
            'Testing',
            '# Foobar',
            'Not Matched',
            ])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=True),
                ['Testing'])

    def test_single_mod_exact(self):
        self.read([
            'Beginning Text',
            '# xyzzy',
            'Testing',
            '# Foobar',
            'Not Matched',
            ])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=True),
                ['Testing'])

    def test_single_mod_fuzzy(self):
        self.read([
            'Beginning Text',
            '# xyzzyz',
            'Testing',
            '# Foobar',
            'Not Matched',
            ])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=True),
                ['Testing'])

    def test_single_mod_default(self):
        self.read([
            'Beginning Text',
            '# Unrelated',
            'Testing',
            '# Foobar',
            'Not Matched',
            ])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=True),
                ['Beginning Text'])

    def test_single_mod_empty(self):
        self.read([])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=True),
                [])

    def test_multi_mod_exact(self):
        self.read([
            'Beginning Text',
            '# xyzzy',
            'Testing',
            '# Foobar',
            'Not Matched',
            ])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=False),
                ['Testing'])

    def test_multi_mod_fuzzy(self):
        self.read([
            'Beginning Text',
            '# xyzzyz',
            'Testing',
            '# Foobar',
            'Not Matched',
            ])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=False),
                ['Testing'])

    def test_multi_mod_nomatch(self):
        self.read([
            'Beginning Text',
            '# Unrelated',
            'Testing',
            '# Foobar',
            'Not Matched',
            ])
        self.assertEqual(self.readme.find_matching('xyzzy', single_mod=False),
                [])
