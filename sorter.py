#!/usr/bin/env python
# vim: set expandtab tabstop=4 shiftwidth=4:

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
