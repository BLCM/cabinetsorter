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
- `appdirs`
- `coverage` (only to run coverage on the unit tests, for development
  purposes.  Not needed just to run.)

TODO
----

- Support doing initial git clones?
- README/Mod Description parsing could probably use some tweaking,
  but will have to do that carefully, of course.
- Update unit tests, they're pretty out of date now
  - Make sure to have tests to explicitly check for MUT categories
    on FT and BLCMM files
  - Make sure to test specifying a filename which doesn't exist
  - Test stripping spaces from category names (silverxpenguin's
    Revalation, for instance)
  - Test escaped quotes in BLCMM top-level category names
  - Test unicode vs. latin1 mod files
  - Test escaped leading hashes in cabinet.info files
  - ModFile sorting (case-insensitive)
  - Angle brackets in `load_unknown`
  - `wiki_filename` processing
  - We've moved to always using full HTML HREFs instead of wiki
    links, when calling `wiki_link`
  - In `ModFile.load_unknown()`, check for FT-style categories
  - Strip square brackets from ASCII art
- Maybe move category list to its own "static" page, so the
  "Contributing" page doesn't have that huge table before the
  instructions?  Or at least move the table down near the bottom?
- Figure out something to do with, for instance, mopioid's
  Phaseclock.  Also Robeth's TimeScale?
- The first time the app is run, without caches to read from, mods
  which share the name of an author will error out instead of being
  generated.  That will get fixed on subsequent runs which do read
  from the cache.  I don't care enough to fix that edge case at the
  moment, but it may bear looking into later.  (vWolvenn's "Tsunami"
  is the only current case of this actually happening.)

License
-------

Borderlands ModCabinet Sorter is licensed under the
[GPLv3 or later](https://www.gnu.org/licenses/quick-guide-gplv3.html).
See [COPYING.txt](COPYING.txt) for the full text of the license.

