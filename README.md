Borderlands ModCabinet Sorter
=============================

This is an attempt to create an automated ModCabinet wiki for the BL2/TPS
mods housed in the BLCMods github.  The current ModCabinet wiki relies on
modders manually updating the entries, and as a result the ModCabinet is
extremely under-populated (to say nothing of the hassle required for the
folks who *do* keep their mods updated on there).

The util will attempt to loop through a local github checkout, looking for
files named `cabinet.info`, which mostly just contain a line per mod in
the same directory which specifies which categories the mod should belong
in.  The app should be able to read in mod summaries both from the mod
files themselves, and from README files stored alongside the mods.

Obviously it's a bit insane to try and write something to parse through a
bunch of effectively freeform text all over the place, but hopefully it
can be wrangled into something useful, which can then be run every 15
minutes or something.

At the moment, this is still very much in development (and as of time of
writing doesn't even attempt to write out any wiki documents of any sort),
so buyer beware.  Once this thing approaches Actual Functionality, this
README will get cleaned up and some actual documentation provided.

Requirements
------------

This is a Python 3 app.  It may work in Python 2 but no attempt has been
made to find out.  Required modules (installable via `pip`, of course):

- `gitpython`
- `Jinja2`
- `python-Levenshtein`
- `coverage` (only to run coverage on the unit tests, for development
  purposes.  Not needed just to run.)

TODO
----

- Handle duplicate mod names; if it's duplicate between BL2 and TPS,
  I'd propose having the TPS one have a "TPS" prefix, but it's also
  not out of the realm of possibility that we may have a duplicate
  within a single game, too...  Perhaps don't worry about *that*
  possibility unless it turns out to be a problem.  Right now the
  second mod will just generate an error and not get a page.
- Pull some of the config stuff out to a config file
- README/Mod Description parsing could probably use some tweaking,
  but will have to do that carefully, of course.
- Proper logging
- Flag to only update if git has updated?
  - We don't want to run after *every* commit, because there could
    be a bunch all at once.  But maybe if we ran every couple of
    minutes, that could at least be an initial gate.  As opposed
    to my original plan of every 10/15/whatever minutes.
- Update unit tests, they're pretty out of date now
  - Make sure to have tests to explicitly check for MUT categories
    on FT and BLCMM files
  - Make sure to test specifying a filename which doesn't exist
  - Test stripping spaces from category names (silverxpenguin's
    Revalation, for instance)
  - Test escaped quotes in BLCMM top-level category names
  - Test unicode vs. latin1 mod files
  - Test escaped leading hashes in cabinet.info files
- Maybe move category list to its own "static" page, so the
  "Contributing" page doesn't have that huge table before the
  instructions?  Or at least move the table down near the bottom?
- If a README file disappears, the mod page should get updated.
- Changelogs should only get attached to single-mod dirs.
- Figure out something to do with, for instance, mopioid's
  Phaseclock.
- Sort case-insensitively
- Bugs to look into once I'm more inclined to do real bugfixing:
  - `expletivedeleted/Slag Fiend` pulls in the mod itself to its
    README, figure that out.
  - Ethel's `King Bonerfart` mod doesn't actually show the README
    contents, though it does link to the README.  It should really
    include the whole file, given that it's just one line...
    - Our Lord's `Gunless Unique Drop Sound Notifier` is doing this
      too, with a more sizeable README
    - I think this is actually due to multi-mod processing, which
      makes sense.  In Ethel's case there's two mods in there For
      Real, and in Our Lord's case it's just specified that way
      'cause that's what would make sense...
  - Greem's ASCII art (in, for instance, `RarityChanges`) has one
    char in it that we don't strip...

License
-------

Borderlands ModCabinet Sorter is licensed under the
[GPLv3 or later](https://www.gnu.org/licenses/quick-guide-gplv3.html).
See [COPYING.txt](COPYING.txt) for the full text of the license.

