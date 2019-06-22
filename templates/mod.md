# {{ mod.mod_title }}

**Author:** {{ authors[mod.mod_author].wiki_link() }}

**Last Updated:** {{ mod.mod_time.strftime('%B %d, %Y') }}

**In Categories:** {{ mod.get_cat_links(cats) }}

## Download Methods

| Site | Notes |
| ---- | ----- |
| [Download from Github]({{ dl_base_url }}/{{ mod.rel_url() }}) | *(right click and choose "Save Link As")* |
| [View on Github]({{ base_url }}/{{ mod.rel_url() }}) | *(right-click on "Raw" or "Download" button and choose "Save Link As" to download)* |
{%- if mod.nexus_link %}
| [Download from Nexus]({{ mod.nexus_link.url }}) | |
{%- endif %}

{#- -------------------- README -------------------- #}

{%- if mod.readme_desc|length > 0 %}

## README

{{ mod.readme_desc|join("\n") }}
{% endif %}

{#- -------------------- In-Mod Description -------------------- #}

{%- if mod.mod_desc|length > 0 %}

## Description (from inside mod)

{{ mod.mod_desc|join("\n") }}
{% endif %}

{#- -------------------- Youtube Links -------------------- #}

{%- if mod.youtube_urls|length > 0 %}

## Youtube Videos

{% for yt in mod.youtube_urls -%}
- {{ yt.wiki_link() }}
{% endfor %}
{%- endif %}

{#- -------------------- Embedded Screenshots -------------------- #}

{%- if mod.screenshots|length > 0 %}

## Screenshots

{% for ss in mod.screenshots -%}
{%- if ss.text %}
{{ ss.text }}:
{%- endif %}
{{ ss.screenshot_embed() }}

{% endfor %}
{%- endif %}

{#- -------------------- Other URLs -------------------- #}

{%- if mod.urls|length > 0 %}

## Other URLs

{% for url in mod.urls -%}
- {{ url.wiki_link() }}
{% endfor %}
{%- endif %}

