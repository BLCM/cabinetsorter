#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import io
import unittest
from cabinetsorter.app import ModFile

class ModFileBLCMMTests(unittest.TestCase):
    """
    Testing importing a BLCMM-formatted file
    """

    def setUp(self):
        """
        Initialize some vars we'll need on every test.  We're fudging the
        BLCMM file format a bit here, which shouldn't matter 'cause our code
        doesn't actually look for any of that stuff.
        """
        self.modfile = ModFile(0)
        self.df = io.StringIO()
        print(' <head>', file=self.df)
        print('  <type name="BL2" offline="false"/>', file=self.df)
        print('  <profiles>', file=self.df)
        print('   <profile name="default" current="true"/>', file=self.df)
        print('  </profiles>', file=self.df)
        print(' </head>', file=self.df)
        print(' <body>', file=self.df)

    def set_df_contents(self, cat_name, lines):
        """
        Sets the contents of the "file" that we're gonna read in
        """
        print('  <category name="{}">'.format(cat_name), file=self.df)
        for line in lines:
            print(line, file=self.df)
        print('  </category>', file=self.df)
        print(' </body>', file=self.df)
        print('</BLCMM>', file=self.df)
        print('', file=self.df)
        print('#Commands:', file=self.df)
        print('set foo bar baz', file=self.df)
        self.df.seek(0)

    def test_load_commentless(self):
        self.set_df_contents('Mod Name', [
            '<category name="Test">',
            '</category>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_title, 'Mod Name')
        self.assertEqual(self.modfile.mod_desc, [])

    def test_single_comment(self):
        self.set_df_contents('Mod Name', [
            '<comment>Testing</comment>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_two_comments(self):
        self.set_df_contents('Mod Name', [
            '<comment>Testing</comment>',
            '<comment>Testing 2</comment>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing', 'Testing 2'])

    def test_two_comments_interrupted(self):
        self.set_df_contents('Mod Name', [
            '<comment>Testing</comment>',
            '<code profiles="default">set foo bar baz</code>',
            '<comment>Testing 2</comment>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_single_comment_inner_category(self):
        self.set_df_contents('Mod Name', [
            '<category name="Test">',
            '<comment>Testing</comment>',
            '</category>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_single_comment_inner_category_2deep(self):
        self.set_df_contents('Mod Name', [
            '<category name="Test">',
            '<category name="Test2">',
            '<comment>Testing</comment>',
            '</category>',
            '</category>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_single_comment_inner_category_after_set(self):
        self.set_df_contents('Mod Name', [
            '<category name="Test">',
            '<code profiles="default">set foo bar baz</code>',
            '<comment>Testing</comment>',
            '</category>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_two_comments_inner_category_after_set_interrupted(self):
        self.set_df_contents('Mod Name', [
            '<category name="Test">',
            '<code profiles="default">set foo bar baz</code>',
            '<comment>Testing</comment>',
            '<code profiles="default">set foo bar baz</code>',
            '<comment>Testing 2</comment>',
            '</category>',
            ])
        self.modfile.load_blcmm(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])
