# One-off rename

This example shows how to rename a single file in the doc site.

## mkdocs.yml

```yaml
{% include "examples/ok-with-rename/mkdocs-test.yml" %}
```

## Input

```
project
│   README.md
|   foo.bar
```

## Output

```
project
│   README.md
|   foo.bar
|
└───site
│   │   index.html
|   |    
|   └───baz
|         │   index.html
```
