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
*just* the category name.  So to put your mod into the "gear-general" category,
the file would just contain the single word:

    gear-general

If you have more than one mod in a directory, you'll have to be a little
more wordy.  For instance, if you've got three files which should all be
in the "gear-general" category, you can list them in `cabinet.info` like so:

    BastardV3.txt: gear-general
    CatO'NineTails.txt: gear-general
    DarlinV2.txt: gear-general

## Assigning Multiple Categories

Mods can also be in multiple categories.  For instance, Apocalyptech's BL2
Better Loot mod fits decently in both the "loot-system" and "cheat" categories,
so its `cabinet.info` file looks like this:

    loot-system, cheat

## Update Frequency

The process which updates the ModCabinet wiki updates every 10 minutes.
You can see when it was last updated by visiting the [[About ModCabinet Wiki]]
page.  That page will also show you any errors which happened during the last
update.  If you had a typo in one of your category names, or something, it will
show up on that page.

## Screenshots and Nexus Mods Links

To link to external resources like screenshots, or to provide an alternate
download to Nexus Mods, simply add in URLs, one per line, beneath the line which
specifies the categories.  That means that a single-mod directory might have
a `cabinet.info` file which looks like this:

    gear-general
    https://i.imgur.com/ClUttYw.gif

Or a directory which has multiple mods might look like this:

    BastardV3.txt: gear-general
    CatO'NineTails.txt: gear-general
    https://i.imgur.com/W5BHeOB.jpg
    DarlinV2.txt: gear-general

You can also add in text labels for your URLs by prefixing them with some text
and separating them with a pipe (`|`) character:

    BastardV3.txt: gear-general
    CatO'NineTails.txt: gear-general
    A pic of the new weapon in action|https://i.imgur.com/W5BHeOB.jpg
    DarlinV2.txt: gear-general

If a URL ends in `.jpg`, `.gif`, or `.png`, it will be embedded into the
cabinet page.  Youtube URLs will be displayed separately from other URLs.

## Comments

Any line which starts with a `#` will be ignored, as will empty lines, so you
can format your `cabinet.info` files a little more nicely, if you want.
For instance, this would be a valid file:

    BastardV3.txt: gear-general

    # Include a screenshot for this one...
    CatO'NineTails.txt: gear-general
    A pic of the new weapon in action|https://i.imgur.com/W5BHeOB.jpg

    DarlinV2.txt: gear-general

## That's it!

Just check in your `cabinet.info` file the exact same way you'd check in a mod
file, and it'll get picked up the next time it's run.  If you have problems,
feel free to stop by [Shadow's Evil Hideout](http://borderlandsmodding.com/community/)
and ask for help.  (Apocalyptech is the maintainer of this code at the moment,
if you wanted to @ him specifically.)
