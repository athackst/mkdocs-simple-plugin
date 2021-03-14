# Extract markdown from a source file

You can even extract markdown from a source file!

See output files [main.md](main.md) and [module.md](module.md)

## mkdocs.yml

```yaml
{% include "examples/ok-source-extract/mkdocs-test.yml" %}
```

## Input

```
project
│   README.md
|   module.py
|   main.c
```

## Output

```
project
│   README.md
|   module.py
|   main.c
|
└───site
│   │   index.html
|   |   
|   └───module
│   │   |    index.html
|   |   
|   └───main
│   │   |    index.html
```
