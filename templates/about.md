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
