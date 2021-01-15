# Use with mkdocstrings

You can even use this with other plugins, like [mkdocstrings](https://pypi.org/project/mkdocstrings/), to achieve advanced configurations.

## Example


The extracted [module documentation](module.md) includes the documentation from the module header, and has invoked mkdocstrings to render api documentation based on Python docstrings.

Compare the webpage linked above with the raw `module.md` generated
by extraction from `module.py`:

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
