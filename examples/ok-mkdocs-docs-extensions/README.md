# Include an extra extension

This example shows how extensions are copied to the result

## Configuration

mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-docs-extensions/mkdocs-test.yml" %}
```

Folder structure:

```
ok-mkdocs-docs-extensions
│   README.md
│   test.txt 
```

## Output

```
ok-mkdocs-docs-extensions
│   README.md
│   test.txt 
│
└───site
│   │   index.html
│   │   test.txt
```
