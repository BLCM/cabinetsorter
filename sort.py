#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

import os
import re
import json
import lzma
import datetime
import collections
import Levenshtein

# TODO: Loop through the git checkout dir and manually assign timestamps based
# on the most recent git commit, since otherwise timestamps are based on when
# they were pulled in to the local filesystem.  Will have to be careful about
# that in the future.  Once this is in a position of running every N minutes
# or whatever, I don't think we'd have to worry about bothering to re-sync
# things after the fact, but we'll need the initial run.  To get the most
# recent commit timestamp from a file, in a format that `touch` recognizes:
#
#    git log -n 1 --format='%cI' filename
#
# To set the timestamp, of course:
#
#    touch -d (date) filename
#
# Or, all at once:
#
#    touch -d "$(git log -n 1 --format='%cI' filename)" filename

# Dirs that we're looking into, and dirs that we're writing to
repo_dir = '/home/pez/git/b2patching/BLCMods.direct'
games = {
        'BL2': 'Borderlands 2 mods',
        'TPS': 'Pre Sequel Mods',
        }
cabinet_dir = '/home/pez/git/b2patching/ModSorted.wiki'
cache_filename = 'modcache.json.xz'

categories = collections.OrderedDict([
        ('general', 'General Gameplay and Balance'),
        ('skills', 'Characters and Skills'),
        ('farming', 'Farming and Looting'),
        ('gear', 'Weapons and Gear'),
        ('tools', 'Tools and Misc'),
        ('gamemodes', 'Game Modes'),
        ('overhauls', 'Overhauls'),
        ('qol', 'Quality of Life'),
        ('skins', 'Visuals and Standalone Skins'),
        ('cheats', 'Cheat Mods'),
        ('wip', 'Works in Progress'),
        ('resources', 'Modder\'s Resources'),
        ])

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

    def __init__(self, dirpath, filenames):
        """
        Initialize given our current dir path, and a list of filenames
        """
        global repo_dir
        self.dirpath = dirpath
        self.rel_dirpath = dirpath[len(repo_dir)+1:]
        path_components = self.rel_dirpath.split(os.sep)
        if len(path_components) > 1:
            self.dir_author = path_components[1]
        else:
            self.dir_author = '(unknown)'
        self.cur_path = path_components[-1]
        self.lower_mapping = {}
        self.extension_map = {}
        self.no_extension = []
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
        global repo_dir
        return (
            self.rel_dirpath,
            self[filename][len(repo_dir)+1:],
            )

class ModFile(object):
    """
    Class to pull info out of a mod file.
    """

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
            with open(self.full_filename) as df:
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

    def add_url(self, url):
        """
        Adds a URL to ourselves, in a temporary fashion (will need
        to "finalize" them once they're done, so we can set
        S_UDPDATED properly, if need be
        """
        self.seen = True
        self.urls.append(url)

    def finalize_urls(self):
        """
        Finalize our URLs, which will put them into the appropriate
        data structures, and also update our status to S_UPDATED if
        need be.
        """
        self.seen = True
        nexus_link = None
        screenshots = []
        for url in self.urls:
            if 'nexusmods.com' in url:
                nexus_link = url
            else:
                screenshots.append(url)
        if (self.status != ModFile.S_NEW and
                (nexus_link != self.nexus_link or screenshots != self.screenshots)):
            self.status = ModFile.S_UPDATED
        self.screenshots = screenshots
        self.nexus_link = nexus_link

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
                if self.re.search(cat_re, line):
                    if 'description' not in self.re.last_match.group(1).lower():
                        return
                elif line.strip().startswith('set '):
                    return
                else:
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

        # Attempt to match on a title, if we can (and return without adding,
        # if that's the case)
        if not self.mod_title and match_title and len(self.mod_desc) == 0:
            if Levenshtein.ratio(match_title.lower(), line.lower()) > .8:
                self.mod_title = line
                return

        # Finally, add it in.
        self.mod_desc.append(line)

class ModCache(object):
    """
    Object to hold info about mod files.
    """

    def __init__(self, filename):
        self.filename = filename
        self.mapping = {}
        if os.path.exists(filename):
            with lzma.open(filename, 'rt', encoding='utf-8') as df:
                serialized_dict = json.load(df)
                for (mod_filename, mod_dict) in serialized_dict.items():
                    self.mapping[mod_filename] = ModFile.unserialize(mod_dict)

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

    def save(self):
        """
        Saves ourself
        """
        save_dict = {}
        for mod_filename, mod in self.mapping.items():
            save_dict[mod_filename] = mod.serialize()
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

# Some initial vars
mod_cache = ModCache(cache_filename)
error_list = []

# Loop through our game dirs
for (game_prefix, game_name) in games.items():
    game_dir = os.path.join(repo_dir, game_name)
    for (dirpath, dirnames, filenames) in os.walk(game_dir):

        # Make a mapping of files by lower-case, so that we can
        # match case-insensitively
        dirinfo = DirInfo(dirpath, filenames)

        # Read our info file, if we have it.
        if 'cabinet.info' in dirinfo:

            # Read the file info
            cabinet_filename = dirinfo['cabinet.info']
            rel_cabinet_filename = cabinet_filename[len(repo_dir)+1:]
            with open(cabinet_filename) as df:
                prev_modfile = None
                for line in df.readlines():
                    if line.strip() == '' or line.startswith('#'):
                        pass
                    elif line.startswith('http://') or line.startswith('https://'):
                        if prev_modfile:
                            prev_modfile.add_url(line.strip())
                        else:
                            error_list.append('ERROR: Did not find previous modfile but got URL, in {}'.format(rel_cabinet_filename))
                    else:
                        if prev_modfile:
                            prev_modfile.finalize_urls()
                        processed_file = None
                        if ': ' in line:
                            (mod_filename, categories) = line.split(': ', 1)
                            processed_file = mod_cache.load(dirinfo, mod_filename)
                        else:
                            categories = line
                            # Scan for which file to use -- just a single mod file in
                            # this dir.  First look for .blcm files.
                            for blcm_file in dirinfo.get_all_with_ext('blcm'):
                                processed_file = mod_cache.load(dirinfo, blcm_file)
                                # We're just going to always take the very first .blcm file we find
                                break

                        # Split up the category list and assign it
                        if processed_file:
                            real_cats = []
                            for name in categories:
                                cats = [c.strip() for c in categories.lower().split(',')]
                                for cat in cats:
                                    if cat in categories:
                                        real_cats.append(cat)
                                    else:
                                        error_list.append('WARNING: Invalid category "{}" in {}'.format(
                                            cat, rel_cabinet_filename,
                                            ))
                            if len(real_cats) == 0:
                                error_list.append('ERROR: No categories found for {}'.format(processed_file.rel_filename))
                                del mod_cache[processed_file.full_filename]
                                prev_modfile = None
                            else:
                                processed_file.set_categories(cats)
                                prev_modfile = processed_file
                        else:
                            error_list.append('ERROR: Mod file not processed in {}'.format(rel_cabinet_filename))

                # Don't forget to finalize the final processed file
                if prev_modfile:
                    prev_modfile.finalize_urls()

# Find any deleted mods.
to_delete = []
for filename, mod in mod_cache.items():
    if not mod.seen:
        to_delete.append(filename)
        error_list.append('NOTICE: Deleting {} - {}'.format(mod.rel_filename, mod.mod_title))
for filename in to_delete:
    del mod_cache[filename]

for mod in mod_cache.values():
    print('{} ({})'.format(mod.rel_filename, ModFile.S_ENG[mod.status]))
    print(mod.mod_title)
    print(mod.mod_author)
    print(mod.mod_time)
    print(mod.mod_desc)
    print('Categories: {}'.format(mod.categories))
    if mod.nexus_link:
        print('Nexus Link: {}'.format(mod.nexus_link))
    if len(mod.screenshots) > 0:
        print('Screenshots:')
        for ss in mod.screenshots:
            print(' * {}'.format(ss))
    print('--')

# Report on any errors
if len(error_list) > 0:
    print('Errors encountered during run:')
    for e in error_list:
        print(' * {}'.format(e))
else:
    print('No errors encountered during run.')

# Write out our mod cache
mod_cache.save()
