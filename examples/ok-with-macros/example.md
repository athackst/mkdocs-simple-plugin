# Example

Here's a printout of the plugin's config file, which I've included using a jinja-style macro.

`````yaml
{% if test %}
{% include "mkdocs.yml" %}
{% endif %}
`````
