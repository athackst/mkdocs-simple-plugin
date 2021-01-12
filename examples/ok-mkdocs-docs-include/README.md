# Only include a subfolder

This example shows how to only include from a specific folder

## Configuration

mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-docs-include/mkdocs-test.yml" %}
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
|   |    index.md
│
└───site
│   │   index.html
|   |   
|   └───draft
│   │   |    index.html
```
