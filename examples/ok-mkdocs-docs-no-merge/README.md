# Don't merge docs folder with other docs

This example shows how to keep the docs folder with your 

## Configuration

mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-docs-no-merge/mkdocs-test.yml" %}
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
│   │   index.html
|   |   
|   └───draft
│   │   |    index.html
|   |   
|   └───test
│   │   |    index.html
|   |  
|   └───index
│   │   |    index.html
```
