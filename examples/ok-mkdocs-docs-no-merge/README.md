<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Don't merge docs folder

## mkdocs.yml

```yaml
# This example shows how to keep the docs folder embedded within your other docs.
site_name: project
plugins:
  - simple:
        merge_docs_dir: false
```
## Input

```
ok-mkdocs-docs-no-merge/
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
├── docs/
│   ├── draft/
│   │   └── index.html
│   └── index.html
├── index.html
└── test/
    └── index.html
```

