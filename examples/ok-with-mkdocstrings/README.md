# Use with mkdocstrings

You can even use this with other plugins, like [mkdocstrings](https://pypi.org/project/mkdocstrings/), to achieve advanced configurations.

See the [example](example.md).

## mkdocs.yml

```yaml
{% include "examples/ok-with-mkdocstrings/mkdocs-test.yml" %}
```

## Input

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
