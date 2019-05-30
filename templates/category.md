# {{ game.title }}: {{ cat.title }} Mods

{{ game.wiki_link_back() }}

{% for mod in mods %}
* {{ mod.wiki_link() }}, by {{ mod.mod_author }}
{%- endfor %}

