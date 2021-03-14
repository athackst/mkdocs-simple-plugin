# Don't merge docs folder with other docs

This example shows how to keep the docs folder embedded within your other docs.

## mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-docs-no-merge/mkdocs-test.yml" %}
```

## Input

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
│   │   index.html  [From README.md]
|   |   
|   └───test
│   │   |    index.html
|   |
|   └───docs
│   │   |    index.html  [From docs/index.md]
|   |   |
|   |   └───draft
│   │   |   |    index.html
```
