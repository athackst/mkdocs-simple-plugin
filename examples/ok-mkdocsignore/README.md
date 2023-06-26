<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Ignore with .mkdocsignore

## mkdocs.yml

```yaml
# Ignore files with a .mkdocsignore file.
site_name: ok-mkdocsignore
plugins:
  - simple
```
## Input

```
ok-mkdocsignore/
├── .mkdocsignore
├── hello/
│   ├── foo/
│   │   ├── bar.md
│   │   └── foo.md
│   ├── hello.md
│   └── world/
│       ├── .mkdocsignore
│       └── world.md
├── mkdocs.yml
├── README.md
└── test/
    ├── bar.md
    └── foo.md
```


**.mkdocsignore**
```
{% raw %}
# Ignore everything in the test folder
test
# Ignore the foo file in hello/foo
hello/foo/foo*

{% endraw %}
```

**hello/world/.mkdocsignore**
```
{% raw %}
# Ignore everything in this folder

{% endraw %}
```


## Output

```
site/
├── .mkdocsignore
├── hello/
│   ├── foo/
│   │   └── bar/
│   │       └── index.html
│   └── hello/
│       └── index.html
└── index.html
```

