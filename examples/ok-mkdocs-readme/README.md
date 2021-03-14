# Only a single readme

This is the simplest documentation site you could have.  It's just a simple readme.

## mkdocs.yml

```yaml
site_name: project
plugins:
  - simple
```

## Input

```
project
│   README.md
```

## Output

```
project
│   README.md
│
└───site
│   │   index.html
```
