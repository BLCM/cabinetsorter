[[← Go Back|Home]]

The ModCabinet wiki exists to provide a slightly-easier way of browsing through
Borderlands 2/TPS mods, apart from digging through the somewhat-daunting main
github repo.  For information on actually building your own mods, the [BLCMods
Wiki](https://github.com/BLCM/BLCMods/wiki) is your best starting point.

The content of this wiki is auto-generated on a regular basis, from
the contents of the main BLCM Github.  The last generation time for
this site was: **{{ gen_time.strftime('%B %d, %Y %I:%M %p %z (%Z)') }}**

## Errors

{% if errors|length > 0 %}
{%- for error in errors %}
- {{ error }}
{%- endfor %}
{% else %}
No errors were encountered while generating the wiki.
{% endif %}

## Code

The code which generates this wiki is freely available under the
[GNU GPLv3 or later](https://www.gnu.org/licenses/quick-guide-gplv3.html),
and is available on [BLCM's cabinetsorter repo](https://github.com/BLCM/cabinetsorter).
I can't imagine it'd be useful for anything but this one specific
purpose, but there it is, anyway.
