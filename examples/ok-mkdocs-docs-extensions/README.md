# Include an extra extension

This example shows how extensions are copied to the result

## mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-docs-extensions/mkdocs-test.yml" %}
```

## Input

```
project
│   README.md
│   test.txt 
```

## Output

```
project
│   README.md
│   test.txt 
│
└───site
│   │   index.html
│   │   test.txt
```
