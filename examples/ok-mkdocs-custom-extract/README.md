# Custom extraction

This example shows how to set up custom extraction modes. Litcoffee files
consist of interspersed Markdown and Coffeescript code. The pattern
defined here extracts a documentation page from each such file, consisting of:
everything from the beginning of the file to the first line of code
(a line indented by at least four spaces), together with any later Markdown
block preceded by a comment containing `# DOCPAGE`.

## mkdocs.yml

```yaml
{% include "examples/ok-mkdocs-custom-extract/mkdocs-test.yml" %}
```

## Input

```
project
│   README.md
│   fibo.litcoffee 
```

## Output

```
project
│   README.md
│   fibo.litcoffee 
│
└───site
│   │   index.html
|   |   
|   └───fibo
│   │   |    index.html
```
