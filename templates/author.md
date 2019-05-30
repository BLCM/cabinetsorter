# Mods by {{ author.name }}

{% for game, modlist in author.mods.items() %}

## {{ games[game].title }}

{% for mod in modlist|sort %}
- {{ mod }}
{%- endfor %}

{% endfor %}
