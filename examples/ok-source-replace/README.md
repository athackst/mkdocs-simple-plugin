# Extract markdown from a source file

You can even replace lines with regex expressions!

## mkdocs.yml

```yaml
{% include "examples/ok-source-replace/mkdocs-test.yml" %}
```

## Input

```
project
│   README.md
|   module.py
```
## Output

```
project
│   README.md
|   module.py
|
└───site
│   │   index.html
|   |   
|   └───module
│   │   |    index.html
```
