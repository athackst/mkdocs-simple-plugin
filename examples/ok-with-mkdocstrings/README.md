# Use with mkdocstrings

You can even use this with other plugins, like [mkdocstrings](https://pypi.org/project/mkdocstrings/) to achieve advanced configurations.

## Example


The extracted module documentation includes the documentation from the module header.

Extracted:

```
{% include "examples/ok-with-mkdocstrings/module.md" %}
```

## Configuration

mkdocs.yml

```yaml
{% include "examples/ok-with-mkdocstrings/mkdocs-test.yml" %}
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
