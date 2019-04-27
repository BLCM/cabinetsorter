#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

import io
import unittest
from cabinetsorter.app import Readme

class ReadmeReadFileObjTests(unittest.TestCase):
    """
    Testing reading our README files
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

    def read(self):
        """
        Read in our file.  Note that the `is_markdown` flag is
        currently not actually used, so we're not bothering to
        test for it at all.
        """
        self.readme.read_file_obj(self.df, False)

    def test_load_empty(self):
        self.set_df_contents([])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            })

    def test_initial_comment(self):
        self.set_df_contents([
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Testing'],
            })

    def test_initial_two_comments(self):
        self.set_df_contents([
            'Testing',
            'Testing 2',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Testing', 'Testing 2'],
            })

    def test_hash_section(self):
        for hashes in ['#', '##', '###', '####']:
            with self.subTest(hashes=hashes):
                self.set_df_contents([
                    '{} Section'.format(hashes),
                    'Testing',
                    ])
                self.read()
                self.assertEqual(self.readme.mapping, {
                    '(default)': [],
                    'section': ['Testing'],
                    })

    def test_default_and_one_hash_section(self):
        self.set_df_contents([
            'Initial',
            '# Section',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Initial'],
            'section': ['Testing'],
            })

    def test_one_hash_section_two_lines(self):
        self.set_df_contents([
            '# Section',
            'Testing',
            'Testing 2',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing', 'Testing 2'],
            })

    def test_double_underline_section(self):
        self.set_df_contents([
            'Section',
            '=======',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing'],
            })

    def test_single_underline_section(self):
        self.set_df_contents([
            'Section',
            '-------',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing'],
            })

    def test_initial_double_line(self):
        self.set_df_contents([
            '=======',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['=======', 'Testing'],
            })

    def test_initial_single_line(self):
        self.set_df_contents([
            '-------',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['-------', 'Testing'],
            })

    def test_dash_section(self):
        self.set_df_contents([
            '- Section',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing'],
            })

    def test_two_sections(self):
        self.set_df_contents([
            '- Section',
            'Testing',
            '# Section 2',
            'More Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing'],
            'section 2': ['More Testing'],
            })

    def test_two_sections_multiline(self):
        self.set_df_contents([
            'Initial',
            'Text',
            '- Section',
            'Testing',
            'Foo',
            '# Section 2',
            'More Testing',
            'Bar',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Initial', 'Text'],
            'section': ['Testing', 'Foo'],
            'section 2': ['More Testing', 'Bar'],
            })

    def test_initial_default_blank(self):
        self.set_df_contents([
            '',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Testing'],
            })

    def test_initial_default_blank_double(self):
        self.set_df_contents([
            '',
            '',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Testing'],
            })

    def test_initial_section_blank(self):
        self.set_df_contents([
            '- Section',
            '',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing'],
            })

    def test_initial_section_blank_double(self):
        self.set_df_contents([
            '- Section',
            '',
            '',
            'Testing',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing'],
            })

    def test_trailing_blank(self):
        self.set_df_contents([
            'Testing',
            '',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Testing'],
            })

    def test_trailing_section_blank(self):
        self.set_df_contents([
            '# Section',
            'Testing',
            '',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': [],
            'section': ['Testing'],
            })

    def test_two_trailing_section_blank(self):
        self.set_df_contents([
            'Main',
            '',
            '# Section',
            'Testing',
            '',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Main'],
            'section': ['Testing'],
            })

    def test_double_trailing_blank(self):
        self.set_df_contents([
            'Testing',
            '',
            '',
            ])
        self.read()
        self.assertEqual(self.readme.mapping, {
            '(default)': ['Testing'],
            })
