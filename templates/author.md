# Mods by {{ author.name }}

{% for game, modlist in author.mods.items() %}

## {{ games[game].title }}

[(Go directly to {{ author.name }}'s {{ games[game].abbreviation }} Github mod directory)]({{ base_url }}/{{ author.rel_url(games[game]) }})

{% for mod in modlist|sort %}
- {{ mod }}
{%- endfor %}

{% endfor %}
