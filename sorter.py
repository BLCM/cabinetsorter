#!/usr/bin/env python
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

from cabinetsorter.app import App

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

if __name__ == '__main__':
    app = App()
    app.run()
