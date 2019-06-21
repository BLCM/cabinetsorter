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

- Improve download buttons/links - I don't really like how they look
  at the moment.  Maybe even use images?
- Handle duplicate mod names; if it's duplicate between BL2 and TPS,
  I'd propose having the TPS one have a "TPS" prefix, but it's also
  not out of the realm of possibility that we may have a duplicate
  within a single game, too...  Perhaps don't worry about *that*
  possibility unless it turns out to be a problem.  Right now the
  second mod will just generate an error and not get a page.
- Pull some of the config stuff out to a config file
- Solidify category list
- README/Mod Description parsing could probably use some tweaking,
  but will have to do that carefully, of course.
- Proper logging
- Show Changelogs for single-mod info files, if found in the README
- Link to full README
- Figure out what to do about links with ampersands in the title
  - Use absolute links, or:
  - Convert the page title to use "and"

License
-------

Borderlands ModCabinet Sorter is licensed under the
[GPLv3 or later](https://www.gnu.org/licenses/quick-guide-gplv3.html).
See [COPYING.txt](COPYING.txt) for the full text of the license.

