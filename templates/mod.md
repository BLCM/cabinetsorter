# {{ mod.mod_title }}

**Author:** {{ mod.mod_author }}
**Last Updated:** {{ mod.mod_time }}

{% if mod.mod_desc|length > 0 %}
## Description
{{ mod.mod_desc|join("\n") }}
{% endif %}

{% if mod.readme_desc|length > 0 %}
## README
{{ mod.readme_desc|join("\n") }}
{% endif %}

## Disclaimer

ModCabinet is auto-generated based on information found in the BLCM Github.  Information
here could be wrong in various ways - if you see a problem, please talk to us at blah blah
blah.
