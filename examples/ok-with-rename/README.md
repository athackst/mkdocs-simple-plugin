<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Rename a file

## mkdocs.yml

```yaml
# This example shows how to rename a single file in the doc site.
site_name: ok-with-rename
plugins:
  - simple:
      semiliterate:
      - pattern: '^foo.bar$'
        destination: baz.md
```
## Input

```
ok-with-rename/
├── foo.bar
├── mkdocs.yml
└── README.md
```



## Output

```
site/
├── baz/
│   └── index.html
└── index.html
```

