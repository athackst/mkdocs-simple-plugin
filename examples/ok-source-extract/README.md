# Extract markdown from a source file

You can even extract markdown from a source file!

## Configuration

mkdocs.yml

```yaml
{% include "examples/ok-source-extract/mkdocs-test.yml" %}
```

Folder structure:

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
