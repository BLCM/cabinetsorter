#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import io
import unittest
from cabinetsorter.app import ModFile

class ModFileFTTests(unittest.TestCase):
    """
    Testing importing a FilterTool-formatted file
    """

    def setUp(self):
        """
        Initialize some vars we'll need on every test.  FT format is not especially
        structured, so not a lot of work to do here.
        """
        self.modfile = ModFile(0)
        self.df = io.StringIO()

    def set_df_contents(self, cat_name, lines):
        """
        Sets the contents of the "file" that we're gonna read in.  We enforce a bit
        of FilterTool-style formatting in here, though it's quite a bit more freeform
        than BLCMM.  There'll be empty lines inbetween everything, though
        """
        print('#<{}>'.format(cat_name), file=self.df)
        print('', file=self.df)
        for line in lines:
            print(line, file=self.df)
            print('', file=self.df)
        print('#</{}>'.format(cat_name), file=self.df)
        print('', file=self.df)
        print('set Transient.SparkServiceConfiguration_6 Keys ("whatever")', file=self.df)
        self.df.seek(0)

    def test_load_commentless(self):
        self.set_df_contents('Mod Name', [
            'set foo bar baz',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_title, 'Mod Name')
        self.assertEqual(self.modfile.mod_desc, [])

    def test_one_comment(self):
        self.set_df_contents('Mod Name', [
            'Testing',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_two_comments(self):
        self.set_df_contents('Mod Name', [
            'Testing',
            'Testing 2',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing', 'Testing 2'])

    def test_two_comments_interrupted(self):
        self.set_df_contents('Mod Name', [
            'Testing',
            'set foo bar baz',
            'Testing 2',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_two_comments_interrupted_cat(self):
        self.set_df_contents('Mod Name', [
            'Testing',
            '#<Category>',
            'Testing 2',
            '#</Category>',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_two_comments_interrupted_hotfix(self):
        self.set_df_contents('Mod Name', [
            'Testing',
            '#<hotfix><key>test</key><value>moretest</value></hotfix>',
            'Testing 2',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

    def test_comment_nested_cat(self):
        self.set_df_contents('Mod Name', [
            '#<Category>',
            'Testing',
            '#</Category>',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_desc, [])

    def test_comment_nested_cat_description(self):
        self.set_df_contents('Mod Name', [
            '#<Description>',
            'Testing',
            '#</Description>',
            ])
        self.modfile.load_ft(self.df)
        self.assertEqual(self.modfile.mod_desc, ['Testing'])

