# Use with the macros plugin

You can even use this with other plugins, like [macros](https://pypi.org/project/mkdocs-macros-plugin/) to achieve advanced configurations.

## Example

Here's a print out of the plugin's config file, which I've included using a jinja-style macro.

```yaml
{% include "mkdocs.yml" %}
```

And the extracted module documentation includes the readme.

extracted:


`````
{% if test %}{% include "module.md" %}
{% else %}{% include "examples/ok-with-macros/module.md" %}
{% endif %}
`````

## Configuration

mkdocs.yml

```yaml
{% if test %}
    {% include "mkdocs-test.yml" %}
{% else %}
    {% include "examples/ok-with-macros/mkdocs-test.yml" %}
{% endif %}
```

Folder structure:

```
project
│   README.md
|   module.py
```

## Output

```
project
│   README.md
|   module.py
|
└───site
│   │   index.html
|   |   
|   └───module
│   │   |    index.html
```
