<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Only include a specific folder

## mkdocs.yml

```yaml
# This example shows how to only include from a specific folder
site_name: project
plugins:
  - simple:
      include_folders: ["./subfolder**"]
```
## Input

```
ok-mkdocs-docs-include/
├── mkdocs.yml
├── README.md
├── subfolder/
│   ├── draft.md
│   └── index.md
└── test.md
```



## Output

```
site/
└── subfolder/
    ├── draft/
    │   └── index.html
    └── index.html
```

