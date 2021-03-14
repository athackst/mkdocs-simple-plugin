# Snippet Extraction

This is useful if you'd like to create a snippet from a file, or rearrange
contents using inclusion.

See output files [module.md](module.md) and [snippet](snippet.md).

## mkdocs.yml

```yaml
{% include "examples/ok-source-with-snippet/mkdocs-test.yml" %}
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
|   |   
|   └───snippet
│   │   |    index.html
```
