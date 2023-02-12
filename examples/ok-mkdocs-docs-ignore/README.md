<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Ignore a folder

## mkdocs.yml

```yaml
# This example shows how a subfolder can be ignored.
site_name: ok-mkdocs-docs-ignore
plugins:
  - simple:
      ignore: ["subfolder"]
```
## Input

```
ok-mkdocs-docs-ignore/
├── mkdocs.yml
├── other-folder/
│   └── subfolder/
│       ├── draft.md
│       └── index.md
├── README.md
├── subfolder/
│   ├── draft.md
│   └── index.md
└── test.md
```



## Output

```
site/
├── index.html
├── other-folder/
│   └── subfolder/
│       ├── draft/
│       │   └── index.html
│       └── index.html
└── test/
    └── index.html
```

