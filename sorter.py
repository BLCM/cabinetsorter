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

import argparse
from cabinetsorter.app import App

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            description='BLCM ModCabinet Auto-Sorter',
            #formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            epilog="""Use the -g/--no-git or -c/--no-commit options to avoid
                git integration, which can be quite useful when you're
                iterating through code/template changes but probably not of
                much use otherwise.  The -i/--initial argument will also do an
                initial "first-time-run" task of looping through the github
                repo setting all file mtimes to be equal to their most-
                recently-updated timestamp in the git tree.
                """
            )

    parser.add_argument('-g', '--no-git',
            dest='do_git',
            action='store_false',
            help='Don\'t interact with git in any way while running (implies --no-commit)',
            )

    parser.add_argument('-c', '--no-commit',
            dest='do_git_commit',
            action='store_false',
            help='Don\'t do any git commit actions after processing.',
            )

    parser.add_argument('-i', '--initial',
            dest='do_initial_tasks',
            action='store_true',
            help='Do some first-time-run initial tasks to get the github repo dir ready',
            )

    args = parser.parse_args()

    app = App()
    app.run(
            do_git=args.do_git,
            do_git_commit=args.do_git_commit,
            do_initial_tasks=args.do_initial_tasks)
