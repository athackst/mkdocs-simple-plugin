# Example

Here's a printout of the plugin's config file, which I've included using a jinja-style macro.

`````yaml
{% if test %}
{% include "mkdocs-test.yml" %}
{% else %}{% include "examples/ok-with-macros/mkdocs-test.yml" %}
{% endif %}
`````

And the extracted module documentation also includes the config file.

extracted:


`````
{% if test %}{% include "module.md" %}
{% else %}{% include "examples/ok-with-macros/module.md" %}
{% endif %}
`````
