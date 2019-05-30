# {{ game.title }}: {{ cat.title }} Mods

{{ game.wiki_link_back() }}

{% for mod in mods %}
- {{ mod.wiki_link() }}, by {{ authors[mod.mod_author].wiki_link() }}
{%- endfor %}

