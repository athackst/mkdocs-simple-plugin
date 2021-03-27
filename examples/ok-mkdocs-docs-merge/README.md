<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Merge into docs folder

## mkdocs.yml

```yaml
# This example shows how to merge a docs folder with other documentation.
site_name: project
plugins:
  - simple
```
## Input

```
ok-mkdocs-docs-merge/
├── docs/
│   ├── draft.md
│   └── index.md
├── mkdocs.yml
├── README.md
└── test.md
```



## Output

```
site/
├── draft/
│   └── index.html
├── index.html
└── test/
    └── index.html
```

