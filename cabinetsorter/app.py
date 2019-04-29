#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright 2019 Christopher J. Kucera
# <cj@apocalyptech.com>
# <http://apocalyptech.com/contact.php>
#
# This file is part of Borderlands ModCabinet Sorter.
#
# Borderlands ModCabinet Sorter is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Borderlands ModCabinet Sorter is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Borderlands ModCabinet Sorter.  If not, see
# <https://www.gnu.org/licenses/>.

import os
import re
import json
import lzma
import datetime
import collections
import Levenshtein

class Re(object):
    """
    Class to allow us to use a Perl-like regex-comparison idiom
    such as:

    if $line =~ /(foo)/ { ... }
    elsif $line =~ /(bar)/ { ... }
    elsif $line =~ /(baz)/ { ... }

    Taken from http://stackoverflow.com/questions/597476/how-to-concisely-cascade-through-multiple-regex-statements-in-python
    """

    def __init__(self):
        self.last_match = None

    def match(self, regex, text):
        self.last_match = regex.match(text)
        return self.last_match

    def search(self, regex, text):
        self.last_match = regex.search(text)
        return self.last_match

class DirInfo(object):
    """
    Class to hold some info about all the files in the current dir,
    and provide some useful methods to get at it.
    """

    def __init__(self, repo_dir, dirpath, filenames):
        """
        Initialize given our current dir path, and a list of filenames
        """
        self.repo_dir = repo_dir
        self.dirpath = dirpath
        self.rel_dirpath = dirpath[len(self.repo_dir)+1:]
        path_components = self.rel_dirpath.split(os.sep)
        if len(path_components) > 1:
            self.dir_author = path_components[1]
        else:
            self.dir_author = '(unknown)'
        self.cur_path = path_components[-1]
        self.lower_mapping = {}
        self.extension_map = {}
        self.no_extension = []
        self.readme = None
        for n in filenames:
            lower = n.lower()
            if '.' in lower:
                ext = lower.split('.')[-1]
                if ext not in self.extension_map:
                    self.extension_map[ext] = [lower]
                else:
                    self.extension_map[ext].append(lower)
            else:
                self.no_extension.append(lower)
            self.lower_mapping[lower] = os.path.join(dirpath, n)

            # We're assuming there'll only be one README in any given
            # dir, which is probably safe enough, and I don't think I
            # care enough to try and prioritize, in dirs where there
            # might be more than one
            if 'readme' in lower:
                self.readme = self.lower_mapping[lower]

    def __getitem__(self, key):
        """
        Pretend to be a dict
        """
        return self.lower_mapping[key.lower()]

    def __contains__(self, key):
        """
        Return whether or not we contain the given filename
        """
        return key.lower() in self.lower_mapping

    def get_all(self):
        """
        Returns all files
        """
        return self.lower_mapping.keys()

    def get_all_with_ext(self, extension):
        """
        Returns all files with the given extension
        """
        if extension in self.extension_map:
            return self.extension_map[extension]
        else:
            return []

    def get_all_no_ext(self):
        """
        Returns all entries without extensions
        """
        return self.no_extension

    def get_rel_path(self, filename):
        """
        Returns a tuple with the relative path to the directory containing
        the given file, and the relative path to the file itself
        """
        return (
            self.rel_dirpath,
            self[filename][len(self.repo_dir)+1:],
            )

class ModFile(object):
    """
    Class to pull info out of a mod file.
    """

    cache_category = 'mods'

    (S_UNKNOWN,
            S_CACHED,
            S_NEW,
            S_UPDATED) = range(4)

    S_ENG = {
            S_UNKNOWN: 'Unknown',
            S_CACHED: 'Cached',
            S_NEW: 'New',
            S_UPDATED: 'Updated',
            }

    def __init__(self, mtime, dirinfo=None, filename=None, initial_status=S_UNKNOWN):
        self.status = initial_status
        self.mtime = mtime
        self.mod_time = datetime.datetime.fromtimestamp(mtime)
        self.mod_title = None
        self.mod_desc = []
        self.readme_desc = []
        self.nexus_link = None
        self.screenshots = []
        self.urls = []
        self.categories = set()
        self.re = Re()

        if dirinfo:
            # This is when we're actually loading from a file
            self.seen = True
            self.full_filename = dirinfo[filename]
            (self.rel_path, self.rel_filename) = dirinfo.get_rel_path(filename)
            self.mod_author = dirinfo.dir_author
            with open(self.full_filename, encoding='latin1') as df:
                first_line = df.readline()
                if first_line.strip() == '':
                    first_line = df.readline()
                if '<BLCMM' in first_line:
                    self.load_blcmm(df)
                elif first_line.startswith('#<'):
                    self.load_ft(df)
                else:
                    self.load_unknown(df)
        else:
            # This is used when deserializing
            self.seen = False
            self.full_filename = None
            self.rel_path = None
            self.rel_filename = None
            self.mod_author = None

        # Clean up any empty lines at the end of our comments
        if len(self.mod_desc) > 0:
            while self.mod_desc[-1] == '':
                self.mod_desc.pop()

    def serialize(self):
        """
        Returns a serializable dict describing ourselves
        """
        # TODO: Should maybe protobuf this stuff for performance...
        return {
                'ff': self.full_filename,
                'rp': self.rel_path,
                'rf': self.rel_filename,
                'a': self.mod_author,
                'm': self.mtime,
                't': self.mod_title,
                'd': self.mod_desc,
                'r': self.readme_desc,
                'n': self.nexus_link,
                's': self.screenshots,
                'c': list(self.categories),
                }

    @staticmethod
    def unserialize(input_dict):
        """
        Creates a new ModFile given the specified serialized dict
        """
        new_file = ModFile(input_dict['m'], initial_status=ModFile.S_CACHED)
        new_file.full_filename = input_dict['ff']
        new_file.rel_path = input_dict['rp']
        new_file.rel_filename = input_dict['rf']
        new_file.mod_author = input_dict['a']
        new_file.mod_title = input_dict['t']
        new_file.mod_desc = input_dict['d']
        new_file.readme_desc = input_dict['r']
        new_file.nexus_link = input_dict['n']
        new_file.screenshots = input_dict['s']
        new_file.categories = set(input_dict['c'])
        return new_file

    def set_categories(self, categories):
        """
        Sets our categories, updating our status if need be
        """
        self.seen = True
        new_cats = set(categories)
        if new_cats != self.categories:
            if self.status != ModFile.S_NEW:
                self.status = ModFile.S_UPDATED
            self.categories = new_cats

    def set_urls(self, urls):
        """
        Finalize our URLs, which will put them into the appropriate
        data structures, and also update our status to S_UPDATED if
        need be.
        """
        self.seen = True
        nexus_link = None
        screenshots = []
        for url in urls:
            if 'nexusmods.com' in url:
                nexus_link = url
            else:
                screenshots.append(url)
        if (self.status != ModFile.S_NEW and
                (nexus_link != self.nexus_link or screenshots != self.screenshots)):
            self.status = ModFile.S_UPDATED
        self.screenshots = screenshots
        self.nexus_link = nexus_link

    def update_readme_desc(self, new_desc):
        """
        Updates our README description with the given array
        """
        self.seen = True
        if self.status != ModFile.S_NEW and new_desc != self.readme_desc:
            self.status = ModFile.S_UPDATED
        self.readme_desc = new_desc

    def load_blcmm(self, df):
        """
        Loads in a BLCMM-formatted file.  The idea is to grab the first category
        name, as the title of the mod, and then the first comment block we find.
        """
        finding_main_cat = True
        reading_comments = False
        cat_re = re.compile('<category name="(.*)">')
        comment_re = re.compile('<comment>(.*)</comment>')
        for line in df.readlines():
            if finding_main_cat:
                if self.re.search(cat_re, line):
                    self.mod_title = self.re.last_match.group(1)
                    finding_main_cat = False
            elif reading_comments:
                if self.re.search(comment_re, line):
                    self.add_comment_line(self.re.last_match.group(1))
                else:
                    # If we got here, we had some comments but found Something Else.
                    # Stop processing at this point
                    return
            else:
                if self.re.search(comment_re, line):
                    reading_comments = True
                    self.add_comment_line(self.re.last_match.group(1))

    def load_ft(self, df):
        """
        Loads in a FilterTool-formatted file.  The idea is to grab the first category
        name, as the title of the mod, and then the first comment block we find.  This
        is a bit trickier than BLCMM files since comments are just plaintext inline
        with everything else.
        """
        df.seek(0)
        finding_main_cat = True
        reading_comments = False
        cat_re = re.compile('#<(.*)>')
        for line in df.readlines():
            if finding_main_cat:
                if self.re.search(cat_re, line):
                    self.mod_title = self.re.last_match.group(1)
                    finding_main_cat = False
            else:
                stripped = line.strip()
                if '#<hotfix>' not in line and self.re.search(cat_re, line):
                    # Unlike the BLCMM processing, at the moment, we're not allowing
                    # comments after nested categories, though we *are* if there's
                    # a "description" folder, since that's a real common way that
                    # FT files get laid out.
                    if 'description' not in self.re.last_match.group(1).lower():
                        return
                elif stripped.startswith('set '):
                    return
                elif stripped.startswith('#<hotfix>'):
                    return
                elif stripped != '':
                    self.add_comment_line(line)

    def load_unknown(self, df):
        """
        Loads in a presumably freeform-text mod.  Mostly just assume everything up to
        the first `set` statement is a comment, I guess.  Initially take the filename
        (minus extension) to be the mod name, but if the first comment line we
        find happens to match close enough to the filename, we'll use that for the 
        title instead.
        """
        temp_mod_name = os.path.split(self.full_filename)[-1].rsplit('.', 1)[0]
        df.seek(0)
        for line in df.readlines():
            if line.strip().startswith('set '):
                break
            else:
                self.add_comment_line(line, match_title=temp_mod_name)
        if not self.mod_title:
            self.mod_title = temp_mod_name

    def add_comment_line(self, comment_line, match_title=None):
        """
        Adds a comment line to our description, attempting to strip out some common
        comment prefixes and do some general data massaging.  If `match_title` isn'
        `None`, and this is the first comment line to be inserted, check to see if
        the line is similar to the given title, and set the mod title to be that
        comment line.
        """

        # Take off any whitespace and comment characters
        line = comment_line.strip("/#\n\r\t ")
        
        # Prevent adding an empty line at the beginning
        if line == '' and len(self.mod_desc) == 0:
            return

        # Prevent adding more than one empty line in a row
        if len(self.mod_desc) > 0 and self.mod_desc[-1] == '' and line == '':
            return

        # Attempt to prevent adding in header ASCII art
        if len(self.mod_desc) == 0 and line.strip("_/\\.:|#~ \t") == '':
            return

        # Attempt to match on a title, if we can (and return without adding,
        # if that's the case)
        if not self.mod_title and match_title and len(self.mod_desc) == 0:
            if Levenshtein.ratio(match_title.lower(), line.lower()) > .8:
                self.mod_title = line
                return

        # Finally, add it in.
        self.mod_desc.append(line)

class Readme(object):
    """
    Class to hold information about README files.  We're mostly just trying
    to find anything that might be a heading or list entry, so we can
    match on it later.  Trying to make this work more or less equally
    well whether it's markdown or plaintext.
    """

    cache_category = 'readmes'

    def __init__(self, mtime, filename=None):
        self.mapping = {'(default)': []}
        self.mtime = mtime
        self.first_section = None
        if filename:
            self.read_file(filename)
            self.filename = filename
        else:
            self.filename = None

    def find_matching(self, mod_name, single_mod=True):
        """
        Tries to find a matching section in the readme, given the specified
        `mod_name`.  If `single_mod` is True, the README is expected to be
        for a single mod in the dir.  If False, it is assumed to be in a dir
        containing multiple mods
        """
        mod_name_lower = mod_name.lower()
        if single_mod:
            if 'overview' in self.mapping:
                return self.mapping['overview']
            for section in self.mapping.keys():
                if Levenshtein.ratio(mod_name_lower, section) > .8:
                    return self.mapping[section]
            if self.first_section:
                return self.mapping[self.first_section]
            else:
                return self.mapping['(default)']
        else:
            for section in self.mapping.keys():
                if Levenshtein.ratio(mod_name_lower, section) > .8:
                    return self.mapping[section]
            return []


    def serialize(self):
        """
        Returns a serializable dict describing ourselves (since we're
        basically just a glorified dict anyway, this is pretty trivial)
        """
        return {
                'f': self.filename,
                'm': self.mtime,
                'd': self.mapping,
                's': self.first_section,
                }

    @staticmethod
    def unserialize(input_dict):
        """
        Creates a new Readme given the specified serialized dict
        """
        new_readme = Readme(input_dict['m'])
        new_readme.filename = input_dict['f']
        new_readme.mapping = input_dict['d']
        new_readme.first_section = input_dict['s']
        return new_readme

    def read_file(self, filename):
        """
        Attempt to parse the given filename
        """
        if filename.lower().endswith('.md'):
            is_markdown = True
        else:
            is_markdown = False
        with open(filename) as df:
            self.read_file_obj(df, is_markdown)

    def read_file_obj(self, df, is_markdown):
        """
        Read our file from an open filehandle.  At the
        moment `is_markdown` isn't actually used anymore,
        though we may want to do that at some point.  This
        was split off from `read_file` mostly just for ease
        of unit-testing.
        """
        prev_line = None
        cur_section = '(default)'
        for line in df.readlines():
            line = line.strip()
            if line.startswith('#'):
                cur_section = line.lstrip("# \t").lower()
                self.mapping[cur_section] = []
            elif line.startswith('==='):
                # Multiline markdown section highlighting.  Annoying!  A
                # shame I personally use it all the time, eh?
                if prev_line:
                    self.mapping[cur_section].pop()
                    if self.first_section == cur_section and len(self.mapping[cur_section]) == 0:
                        self.first_section = None
                    cur_section = prev_line.strip().lower()
                    self.mapping[cur_section] = []
                else:
                    if not self.first_section:
                        self.first_section = cur_section
                    self.mapping[cur_section].append(line)
            elif line.startswith('---'):
                # Multiline markdown section highlighting.  Annoying!  A
                # shame I personally use it all the time, eh?
                if prev_line:
                    self.mapping[cur_section].pop()
                    if self.first_section == cur_section and len(self.mapping[cur_section]) == 0:
                        self.first_section = None
                    cur_section = prev_line.strip().lower()
                    self.mapping[cur_section] = []
                else:
                    if not self.first_section:
                        self.first_section = cur_section
                    self.mapping[cur_section].append(line)
            elif line.startswith('-'):
                cur_section = line.lstrip("- \t").lower()
                self.mapping[cur_section] = []
            else:
                if len(self.mapping[cur_section]) > 0 or line != '':
                    if not self.first_section:
                        self.first_section = cur_section
                    self.mapping[cur_section].append(line)
            prev_line = line

        # Get rid of any trailing empty lines in each section
        for (section, data) in self.mapping.items():
            while len(data) > 0 and data[-1] == '':
                data.pop()

class ModCache(object):
    """
    Class to hold info about mod files (and, incidentally, README files).
    """

    def __init__(self, filename):
        self.filename = filename
        self.mapping = {}
        if os.path.exists(filename):
            with lzma.open(filename, 'rt', encoding='utf-8') as df:
                serialized_dict = json.load(df)
                for (mod_filename, mod_dict) in serialized_dict['mods'].items():
                    self.mapping[mod_filename] = ModFile.unserialize(mod_dict)
                for (readme_filename, readme_dict) in serialized_dict['readmes'].items():
                    self.mapping[readme_filename] = Readme.unserialize(readme_dict)

    def load(self, dirinfo, filename):
        """
        Loads a ModFile from the given `filename` (using `dirinfo` as its base),
        if its mtime has been changed or was not previously known.  Otherwise
        return our previously-cached version
        """
        full_filename = dirinfo[filename]
        mtime = os.stat(full_filename).st_mtime
        if full_filename not in self.mapping or mtime != self.mapping[full_filename].mtime:
            if full_filename not in self.mapping:
                initial_status = ModFile.S_NEW
            else:
                initial_status = ModFile.S_UPDATED
            self.mapping[full_filename] = ModFile(mtime, dirinfo, filename, initial_status)
        return self.mapping[full_filename]

    def load_readme(self, filename):
        """
        Loads a README from the given `filename` (which should be a full path).
        """
        mtime = os.stat(filename).st_mtime
        if filename not in self.mapping or mtime != self.mapping[filename].mtime:
            self.mapping[filename] = Readme(mtime, filename)
        return self.mapping[filename]

    def save(self):
        """
        Saves ourself
        """
        save_dict = {'mods': {}, 'readmes': {}}
        for mod_filename, mod in self.mapping.items():
            save_dict[mod.cache_category][mod_filename] = mod.serialize()
        with lzma.open(self.filename, 'wt', encoding='utf-8') as df:
            json.dump(save_dict, df)

    def items(self):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return self.mapping.items()

    def values(self):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return self.mapping.values()

    def keys(self):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return self.mapping.keys()

    def __getitem__(self, key):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return self.mapping[key]

    def __contains__(self, key):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return key in self.mapping

    def __delitem__(self, key):
        """
        Convenience function to be able to use this sort of like a dict
        """
        del self.mapping[key]

class CabinetModInfo(object):
    """
    A little class to hold info about a single mod definition inside
    a `cabinet.info` file.  Just a glorified dictionary, really.  I'd
    use a namedtuple, but we need to be able to dynamically add to
    the 'urls' array
    """

    def __init__(self, filename, categories):
        self.filename = filename
        self.categories = categories
        self.urls = []
    
    def add_url(self, url):
        self.urls.append(url)

class CabinetInfo(object):
    """
    Simple little class to read in and parse our `cabinet.info` files
    """

    def __init__(self, rel_filename, error_list, valid_categories, filename=None):
        """
        Initialize with the given `rel_filename`, which is the filename that
        will be reported in error messages.  Errors encountered while loading
        will be appended to `error_list`.  Valid categories for mods to live in
        is specified by `valid_categories` (should be an object which can be
        checked via `in`, such as a set, or a dict whose keys are the category
        names).  Optionally specify `filename` to actually load the data right
        away.
        """
        self.rel_filename = rel_filename
        self.error_list = error_list
        self.valid_categories = valid_categories
        self.mods = {}
        self.single_mod = False
        if filename:
            self.load_from_filename(filename)

    def load_from_filename(self, filename):
        """
        Load from the given filename
        """
        with open(filename) as df:
            self.load_from_file(df)

    def load_from_file(self, df):
        """
        Loads our information from the given `filename`.  `rel_filename` will
        be the filename reported in errors, if we run into any, and should have
        any unneeded prefixes already shaved off.
        """
        prev_modfile = None
        single_mod = False

        # Now read cabinet.info to find mod files
        for line in df.readlines():
            if line.strip() == '' or line.startswith('#'):
                pass
            elif line.startswith('http://') or line.startswith('https://'):
                if prev_modfile in self.mods:
                    self.mods[prev_modfile].add_url(line.strip())
                else:
                    self.error_list.append('ERROR: Did not find previous modfile but got URL, in {}'.format(
                        self.rel_filename))
            else:
                if ': ' in line:
                    if self.single_mod:
                        self.error_list.append('ERROR: Unknown line "{}" found in single-mod info file {}'.format(
                            line.strip(), self.rel_filename))
                    else:
                        (mod_filename, mod_categories) = line.split(': ', 1)
                        if self.register(mod_filename, mod_categories):
                            prev_modfile = mod_filename
                else:
                    if len(self.mods) > 0:
                        self.error_list.append('ERROR: Unknown line "{}" inside {}'.format(
                            line.strip(), self.rel_filename))
                    else:
                        self.single_mod = True
                        if self.register(None, line.strip()):
                            prev_modfile = None

    def register(self, mod_name, mod_categories):
        """
        Registers a mod line that we've found in a `cabinet.info` file.
        Will double-check against the list of valid categories and return
        False if the mod was not registered.
        """

        # First check to make sure we don't already have this mod
        if mod_name in self.mods:
            self.error_list.append('ERROR: {} specified twice inside {}'.format(
                mod_name, self.rel_filename))
            return False

        # Split up the category list and assign it
        real_cats = []
        cats = [c.strip() for c in mod_categories.lower().split(',')]
        for cat in cats:
            if cat in self.valid_categories:
                real_cats.append(cat)
            else:
                self.error_list.append('WARNING: Invalid category "{}" in {}'.format(
                    cat, self.rel_filename,
                    ))

        # If we have categories which are valid, continue!
        if len(real_cats) > 0:
            self.mods[mod_name] = CabinetModInfo(mod_name, real_cats)
            return True
        else:
            if mod_name:
                report = mod_name
            else:
                report = 'the mod'
            self.error_list.append('ERROR: No categories found for {} in {}'.format(report, self.rel_filename))
            return False

    def modlist(self):
        """
        Returns our list if CabinetModInfo objects
        """
        return self.mods.values()

    def __getitem__(self, key):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return self.mods[key]

    def __contains__(self, key):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return key in self.mods

    def __len__(self):
        """
        Convenience function to be able to use this sort of like a dict
        """
        return len(self.mods)

class App(object):
    """
    Main app
    """

    # Dirs that we're looking into, and dirs that we're writing to
    repo_dir = '/home/pez/git/b2patching/BLCMods.direct'
    games = {
            'BL2': 'Borderlands 2 mods',
            'TPS': 'Pre Sequel Mods',
            }
    cabinet_dir = '/home/pez/git/b2patching/ModSorted.wiki'
    cache_filename = 'cache/modcache.json.xz'
    readme_cache_filename = 'cache/readmecache.json.xz'

    categories = collections.OrderedDict([
            ('general', 'General Gameplay and Balance'),
            ('skills', 'Characters and Skills'),
            ('farming', 'Farming and Looting'),
            ('gear', 'Weapons and Gear'),
            ('tools', 'Tools and Misc'),
            ('gamemodes', 'Game Modes'),
            ('overhaul', 'Overhauls'),
            ('qol', 'Quality of Life'),
            ('skins', 'Visuals and Standalone Skins'),
            ('cheats', 'Cheat Mods'),
            ('wip', 'Works in Progress'),
            ('resources', 'Modder\'s Resources'),
            ('misc', 'Miscellaneous Mods'),
            ])

    def __init__(self):

        # Some initial vars
        self.mod_cache = ModCache(self.cache_filename)
        self.readme_cache = ModCache(self.readme_cache_filename)
        self.error_list = []

    def run(self):
        """
        Run the app
        """

        # Loop through our game dirs
        for (game_prefix, game_name) in self.games.items():
            game_dir = os.path.join(self.repo_dir, game_name)
            for (dirpath, dirnames, filenames) in os.walk(game_dir):

                # Make a mapping of files by lower-case, so that we can
                # match case-insensitively
                dirinfo = DirInfo(self.repo_dir, dirpath, filenames)

                # Read our info file, if we have it.
                if 'cabinet.info' in dirinfo:

                    # Load in readme info, if we can.
                    readme = None
                    if dirinfo.readme:
                        readme = self.readme_cache.load_readme(dirinfo.readme)

                    # Read the file info
                    cabinet_filename = dirinfo['cabinet.info']
                    rel_cabinet_filename = cabinet_filename[len(self.repo_dir)+1:]
                    cabinet_info = CabinetInfo(
                            rel_cabinet_filename,
                            self.error_list,
                            self.categories,
                            filename=cabinet_filename,
                            )

                    # Loop through the mods described by cabinet.info and load them
                    processed_files = []
                    if cabinet_info.single_mod:
                        cabinet_info_mod = cabinet_info.mods[None]
                        # Scan for which file to use -- just a single mod file in
                        # this dir.  First look for .blcm files.
                        for blcm_file in dirinfo.get_all_with_ext('blcm'):
                            processed_files.append((cabinet_info_mod, self.mod_cache.load(dirinfo, blcm_file)))
                            # We're just going to always take the very first .blcm file we find
                            break
                        if len(processed_files) == 0:
                            for txt_file in dirinfo.get_all_with_ext('txt'):
                                if 'readme' not in txt_file.lower():
                                    processed_files.append((cabinet_info_mod, self.mod_cache.load(dirinfo, txt_file)))
                                    # Again, just grab the first one
                                    break
                        if len(processed_files) == 0:
                            for random_file in dirinfo.get_all():
                                if 'readme' not in random_file.lower():
                                    processed_files.append((cabinet_info_mod, self.mod_cache.load(dirinfo, random_file)))
                                    # Again, just grab the first one
                                    break
                    else:
                        for cabinet_info_mod in cabinet_info.modlist():
                            processed_files.append((cabinet_info_mod, self.mod_cache.load(dirinfo, cabinet_info_mod.filename)))

                    # Do Stuff with each file we got
                    for (cabinet_info_mod, processed_file) in processed_files:

                        # See if we've got a "better" description in a readme
                        if readme:
                            readme_info = readme.find_matching(processed_file.mod_title, cabinet_info.single_mod)
                        else:
                            readme_info = []
                        processed_file.update_readme_desc(readme_info)

                        # Set our categories (if we'd read from cache, they may have changed)
                        processed_file.set_categories(cabinet_info_mod.categories)

                        # Set our URLs (likewise, if from cache then they may have changed)
                        processed_file.set_urls(cabinet_info_mod.urls)

        # Find any deleted mods.
        to_delete = []
        for filename, mod in self.mod_cache.items():
            if not mod.seen:
                to_delete.append(filename)
                self.error_list.append('NOTICE: Deleting {} - {}'.format(mod.rel_filename, mod.mod_title))
        for filename in to_delete:
            del self.mod_cache[filename]

        for mod in self.mod_cache.values():
            if mod.status == ModFile.S_NEW or mod.status == ModFile.S_UPDATED:
                print('{} ({})'.format(mod.rel_filename, ModFile.S_ENG[mod.status]))
                print(mod.mod_title)
                print(mod.mod_author)
                print(mod.mod_time)
                print(mod.mod_desc)
                print(mod.readme_desc)
                print('Categories: {}'.format(mod.categories))
                if mod.nexus_link:
                    print('Nexus Link: {}'.format(mod.nexus_link))
                if len(mod.screenshots) > 0:
                    print('Screenshots:')
                    for ss in mod.screenshots:
                        print(' * {}'.format(ss))
                print('--')

        # Report on any errors
        if len(self.error_list) > 0:
            print('Errors encountered during run:')
            for e in self.error_list:
                print(' * {}'.format(e))
        else:
            print('No errors encountered during run.')

        # Write out our mod cache
        self.mod_cache.save()
        self.readme_cache.save()
