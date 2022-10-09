<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Extra extensions

## mkdocs.yml

```yaml
# This example shows how extensions are copied to the result
site_name: ok-mkdocs-docs-extensions
plugins:
  - simple:
      include_extensions: [".txt"]
```
## Input

```
ok-mkdocs-docs-extensions/
├── mkdocs.yml
├── README.md
└── test.txt
```



## Output

```
site/
├── index.html
└── test.txt
```

