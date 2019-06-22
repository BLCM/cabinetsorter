[[← Go Back|Home]]

Contributing to the ModCabinet wiki is quite easy if you've already checked
in your mod to the Github.  Just include a file named `cabinet.info` alongside
your mod(s) to specify the category you'd like to use for the mods.  The
current valid categories are:

| Category Name | Description |
| --- | --- |
{%- for catname, cat in categories.items() %}
| `{{ catname }}` | {{ cat.full_title }}
{%- endfor %}

## Assigning Categories

If you have only one mod per directory, the `cabinet.info` file can contain
*just* the category name.  So to put your mod into the "gear" category,
the file would just contain the single word:

    gear

If you have more than one mod in a directory, you'll have to be a little
more wordy.  For instance, if you've got three files which should all be
in the "gear" category, you can list them in `cabinet.info` like so:

    BastardV3.txt: gear
    CatO'NineTails.txt: gear
    DarlinV2.txt: gear

## Assigning Multiple Categories

Mods can also be in multiple categories.  For instance, Apocalyptech's BL2
Better Loot mod fits decently in both the "cheats" and "farming" categories,
so its `cabinet.info` file looks like this:

    cheats, farming

## Update Frequency

The process which updates the ModCabinet wiki updates every **(omg figure out
the update frequency)**.  You can see when it was last updated by visiting
the [[About ModCabinet Wiki]] page.  That page will also show you any errors
which happened during the last update.  If you had a typo in one of your
category names, or something, it will show up on that page.

## Screenshots and Nexus Mods Links

To link to external resources like screenshots, or to provide an alternate
download to Nexus Mods, simply add in URLs, one per line, beneath the line which
specifies the categories.  That means that a single-mod directory might have
a `cabinet.info` file which looks like this:

    gear
    https://i.imgur.com/ClUttYw.gif

Or a directory which has multiple mods might look like this:

    BastardV3.txt: gear
    CatO'NineTails.txt: gear
    https://i.imgur.com/W5BHeOB.jpg
    DarlinV2.txt: gear

You can also add in text labels for your URLs by prefixing them with some text
and separating them with a pipe (`|`) character:

    BastardV3.txt: gear
    CatO'NineTails.txt: gear
    A pic of the new weapon in action|https://i.imgur.com/W5BHeOB.jpg
    DarlinV2.txt: gear

If a URL ends in `.jpg`, `.gif`, or `.png`, it will be embedded into the
cabinet page.  Youtube URLs will be displayed separately from other URLs.

## That's it!

Just check in your `cabinet.info` file the exact same way you'd check in a mod
file, and it'll get picked up the next time it's run.  If you have problems,
feel free to stop by [Shadow's Evil Hideout](http://borderlandsmodding.com/community/)
and ask for help.  (Apocalyptech is the maintainer of this code at the moment,
if you wanted to @ him specifically.)
