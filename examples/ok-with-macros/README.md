# Extract docs with Macros

You can even use this with other plugins, like [macros](https://pypi.org/project/mkdocs-macros-plugin/) to achieve advanced configurations.

See the [example](example.md).

## mkdocs.yml

```yaml
{% include "examples/ok-with-macros/mkdocs-test.yml" %}
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
