# {{ mod.mod_title }}

**Author:** {{ mod.mod_author }}

**Last Updated:** {{ mod.mod_time.strftime('%B %d, %Y') }}

**In Categories:** {{ mod.get_cat_links(cats) }}

## Download Methods

| Site | Notes |
| ---- | ----- |
| [Download from Github]({{ dl_base_url }}/{{ mod.rel_url() }}) | *(right click and choose "Save Link As")* |
| [View on Github]({{ base_url }}/{{ mod.rel_url() }}) | *(right-click on "Raw" or "Download" button and choose "Save Link As" to download)* |
{%- if mod.nexus_link %}
| [Download from Nexus]({{ mod.nexus_link }}) | |
{%- endif %}

{% if mod.mod_desc|length > 0 %}
## Description
{{ mod.mod_desc|join("\n") }}
{% endif %}

{% if mod.readme_desc|length > 0 %}
## README
{{ mod.readme_desc|join("\n") }}
{% endif %}

{% if mod.screenshots|length > 0 %}
## Screenshots
{% for ss in mod.screenshots %}
* {{ ss }}
{% endfor %}
{% endif %}

## Disclaimer

ModCabinet is auto-generated based on information found in the BLCM Github.  Information
here could be wrong in various ways - if you see a problem, please talk to us at blah blah
blah.
