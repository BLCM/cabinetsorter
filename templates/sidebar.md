**Wiki Links**

- [[Main Page|Home]]
- [[About ModCabinet Wiki]]

{%- for game in games %}

**{{ game.title }} Mods**

{%- for cat in seen_cats[game.abbreviation] %}
- {{ cats[cat].wiki_link(game) }}
{%- endfor %}

{% endfor %}

