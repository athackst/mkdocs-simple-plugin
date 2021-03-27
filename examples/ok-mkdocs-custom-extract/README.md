<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Front matter extraction

## mkdocs.yml

```yaml
# This example shows how to set up custom extraction modes. Litcoffee files
# consist of interspersed Markdown and Coffeescript code. The pattern
# defined here extracts a documentation page from each such file, consisting of:
# everything from the beginning of the file to the first line of code
# (a line indented by at least four spaces), together with any later Markdown
# block preceded by a comment containing `# DOCPAGE`.
site_name: Custom Extraction
plugins:
  - simple:
      semiliterate:
        - pattern: '\.litcoffee'
          extract:
            - {stop: '^\s{4,}\S'}  # No start, so active from beginning
            - {start: '# DOCPAGE', stop: '^\s{4,}\S'}
```
## Input

```
ok-mkdocs-custom-extract/
├── fibo.litcoffee
├── mkdocs.yml
└── README.md
```


**fibo.litcoffee**
```.litcoffee
{% raw %}
This paragraph is here to make sure the extraction starts immediately.
# Coffee Fibonacci

Although trite, this is an example of the sum recurrence.

    fib = (n) ->
      # Base cases
      if n in [ 1 , 2 ]
        return 1
      # Recursive calls
      fib(n-1) + fib(n-2)

## Example usage
This is perfectly good Markdown commentary, but will not appear in the
extracted doc page.

    fib(3) # => fib(2) + fib(1) => 2

    # DOCPAGE
## Complexity
This note about complexity will appear in the doc page.

{% endraw %}
```


## Output

```
site/
├── fibo/
│   └── index.html
└── index.html
```


<div class="admonition quote">
<p class="admonition-title">fibo</p>
<p>This paragraph is here to make sure the extraction starts immediately.</p>
<h1 id="coffee-fibonacci">Coffee Fibonacci</h1>
<p>Although trite, this is an example of the sum recurrence.</p>
<h2 id="complexity">Complexity</h2>
<p>This note about complexity will appear in the doc page.</p></div>
