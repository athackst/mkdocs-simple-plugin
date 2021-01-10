# Ignore a folder

This example shows how a subfolder can be ignored.

## Configuration

mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-docs-ignore/mkdocs-test.yml" %}
```

Folder structure:

```
project
│   README.md
|   test.md
|
└───subfolder
|   |    draft.md
|   |    index.md
```

## Output

```
project
│   README.md
|   test.md
|
└───subfolder
|   |    draft.md
|   |    index.md README.md 
│
└───site
│   │   index.html
|   |   
|   └───test
│   │   |    index.html
```
