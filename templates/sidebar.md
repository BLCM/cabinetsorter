**Wiki Links**

- [[Main Page|Home]]
- [[About ModCabinet Wiki]]
- [[Contributing to ModCabinet]]

{%- for game in games %}

**{{ game.title }} Mods**

{%- for cat in seen_cats[game.abbreviation] %}
{%- if cats[cat].prefix and (not loop.previtem or not cats[loop.previtem].prefix or (cats[loop.previtem].prefix != cats[cat].prefix)) %}
- {{ cats[cat].prefix }}
{%- endif %}
{%- if cats[cat].prefix %}
  - {{ cats[cat].wiki_link(game) }}
{%- else %}
- {{ cats[cat].wiki_link(game) }}
{%- endif %}
{%- endfor %}

{% endfor %}

