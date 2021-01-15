# Merge docs folder with other docs

This example shows how to merge a docs folder with other documentation.

## Configuration

mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-docs-merge/mkdocs-test.yml" %}
```

Folder structure:

```
project
│   README.md
|   test.md
|
└───docs
|   |    draft.md
|   |    index.md
```

## Output

```
project
│   README.md
|   test.md
|
└───docs
|   |    draft.md
|   |    index.md
│
└───site
│   │   index.html  [From docs/index.md, _not_ from README]
|   |   
|   └───draft
│   │   |    index.html
|   |   
|   └───test
│   │   |    index.html
```
