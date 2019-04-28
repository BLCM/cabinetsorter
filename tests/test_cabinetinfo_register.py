#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from cabinetsorter.app import CabinetInfo

class CabinetInfoRegisterTests(unittest.TestCase):
    """
    Testing registering mods inside CabinetInfo
    """

    valid_cats = {
            'cat1': 'Category One',
            'cat2': 'Category Two',
            }

    def setUp(self):
        """
        Initialize some vars we'll need on every test.
        """
        self.errors = []
        self.info = CabinetInfo('cabinet.info', self.errors, self.valid_cats)

    def test_single_cat(self):
        self.assertEqual(self.info.register('xyzzy', 'cat1'), True)
        self.assertIn('xyzzy', self.info)
        self.assertEqual(self.info['xyzzy'].urls, [])
        self.assertEqual(self.info['xyzzy'].categories, ['cat1'])
        self.assertEqual(len(self.errors), 0)

    def test_two_cats(self):
        self.assertEqual(self.info.register('xyzzy', 'cat1, cat2'), True)
        self.assertIn('xyzzy', self.info)
        self.assertEqual(self.info['xyzzy'].urls, [])
        self.assertEqual(self.info['xyzzy'].categories, ['cat1', 'cat2'])
        self.assertEqual(len(self.errors), 0)

    def test_two_cats_strange_whitespace(self):
        self.assertEqual(self.info.register('xyzzy', '   cat1,   cat2 '), True)
        self.assertIn('xyzzy', self.info)
        self.assertEqual(self.info['xyzzy'].urls, [])
        self.assertEqual(self.info['xyzzy'].categories, ['cat1', 'cat2'])
        self.assertEqual(len(self.errors), 0)

    def test_duplicate_mod(self):
        self.assertEqual(self.info.register('xyzzy', 'cat1'), True)
        self.assertIn('xyzzy', self.info)
        self.assertEqual(len(self.errors), 0)
        self.assertEqual(self.info.register('xyzzy', 'cat2'), False)
        self.assertEqual(len(self.errors), 1)
        self.assertIn('specified twice', self.errors[0])

    def test_invalid_category_no_valid(self):
        self.assertEqual(self.info.register('xyzzy', 'cat3'), False)
        self.assertNotIn('xyzzy', self.info)
        self.assertEqual(len(self.errors), 2)
        self.assertIn('Invalid category', self.errors[0])
        self.assertIn('No categories', self.errors[1])
        self.assertIn('xyzzy', self.errors[1])

    def test_invalid_category_one_valid(self):
        self.assertEqual(self.info.register('xyzzy', 'cat1, cat3'), True)
        self.assertIn('xyzzy', self.info)
        self.assertEqual(len(self.errors), 1)
        self.assertIn('Invalid category', self.errors[0])
        self.assertEqual(self.info['xyzzy'].categories, ['cat1'])

    def test_no_mod_name_no_categories(self):
        """
        This one's weird, just testing that we say "the mod" when there's
        no actual name to report
        """
        self.assertEqual(self.info.register(None, 'cat3'), False)
        self.assertEqual(len(self.errors), 2)
        self.assertIn('the mod', self.errors[1])

    def test_modlist(self):
        """
        This doesn't strictly-speaking belong here, but whatever.  Not
        worth doing its own class for
        """
        self.assertEqual(self.info.register('mod', 'cat1'), True)
        self.assertEqual(len(self.info.modlist()), 1)
        self.assertIn(self.info['mod'], self.info.modlist())
