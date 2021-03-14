# Just a docs folder

This example shows how this plugin can be used with just a docs directory

## mkdocs.yml

```yaml
site_name: project
plugins:
  - simple
```

## Input

```
project
│
└───docs
│   │   README.md
```

## Output

```
project
│
└───docs
│   │   README.md 
│
└───site
│   │   index.html
```
