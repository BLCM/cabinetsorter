#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from cabinetsorter.app import ModFile

class ModFileCommentTests(unittest.TestCase):

    def setUp(self):
        """
        Initialize some vars we'll need on every test
        """
        self.modfile = ModFile(0)

    def test_add_comment_line_blank(self):
        self.modfile.add_comment_line('')
        self.assertEqual(self.modfile.mod_desc, [])

    def test_add_comment_line_single(self):
        self.modfile.add_comment_line('testing')
        self.assertEqual(self.modfile.mod_desc, ['testing'])
