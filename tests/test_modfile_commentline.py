#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest
from cabinetsorter.app import ModFile

class ModFileCommentTests(unittest.TestCase):
    """
    Testing our add_comment_line method
    """

    def setUp(self):
        """
        Initialize some vars we'll need on every test
        """
        self.modfile = ModFile(0)

    def test_blank(self):
        self.modfile.add_comment_line('')
        self.assertEqual(self.modfile.mod_desc, [])

    def test_single(self):
        self.modfile.add_comment_line('testing')
        self.assertEqual(self.modfile.mod_desc, ['testing'])

    def test_strips(self):
        for char in ['/', '#', ' ', "\n", "\r", "\t"]:
            with self.subTest(char=char):
                self.modfile = ModFile(0)
                self.modfile.add_comment_line('{}testing{}'.format(char, char))
                self.assertEqual(self.modfile.mod_desc, ['testing'])

    def test_all_strips(self):
        self.modfile.add_comment_line("/#\n\r\t testing/#\n\r\t")
        self.assertEqual(self.modfile.mod_desc, ['testing'])

    def test_two(self):
        self.modfile.add_comment_line('testing')
        self.modfile.add_comment_line('testing2')
        self.assertEqual(self.modfile.mod_desc, ['testing', 'testing2'])

    def test_double_empty(self):
        self.modfile.add_comment_line('testing')
        self.modfile.add_comment_line('')
        self.modfile.add_comment_line('')
        self.assertEqual(self.modfile.mod_desc, ['testing', ''])

    def test_initial_ascii_art(self):
        for char in ['_', '/', '\\', '.', ':', '|', '#', '~', ' ', "\t"]:
            with self.subTest(char=char):
                self.modfile = ModFile(0)
                self.modfile.add_comment_line(char)
                self.assertEqual(self.modfile.mod_desc, [])

    def test_after_ascii_art_no_whitespace_or_comments(self):
        for char in ['_', '\\', '.', ':', '|', '~']:
            with self.subTest(char=char):
                self.modfile = ModFile(0)
                self.modfile.add_comment_line('testing')
                self.modfile.add_comment_line(char)
                self.assertEqual(self.modfile.mod_desc, ['testing', char])

    def test_initial_ascii_art_all(self):
        self.modfile.add_comment_line("_/\\.:| \t#~")
        self.assertEqual(self.modfile.mod_desc, [])

    def test_initial_ascii_art_after(self):
        art = "_/\\.:|# \t~"
        self.modfile.add_comment_line('testing')
        self.modfile.add_comment_line(art)
        self.assertEqual(self.modfile.mod_desc, ['testing', art])

    def test_matched_title(self):
        title = 'Mod Title'
        self.assertEqual(self.modfile.mod_title, None)
        self.modfile.add_comment_line(title, match_title=title)
        self.assertEqual(self.modfile.mod_title, title)
        self.assertEqual(self.modfile.mod_desc, [])

    def test_close_title(self):
        title = 'Mod Title'
        self.assertEqual(self.modfile.mod_title, None)
        self.modfile.add_comment_line(title, match_title='{}z'.format(title))
        self.assertEqual(self.modfile.mod_title, title)
        self.assertEqual(self.modfile.mod_desc, [])

    def test_unmatched_title(self):
        title = 'Mod Title'
        self.assertEqual(self.modfile.mod_title, None)
        self.modfile.add_comment_line(title, match_title='Totally Different')
        self.assertEqual(self.modfile.mod_title, None)
        self.assertEqual(self.modfile.mod_desc, [title])

    def test_matched_title_not_first(self):
        title = 'Mod Title'
        self.assertEqual(self.modfile.mod_title, None)
        self.modfile.add_comment_line('testing')
        self.modfile.add_comment_line(title, match_title=title)
        self.assertEqual(self.modfile.mod_title, None)
        self.assertEqual(self.modfile.mod_desc, ['testing', title])
