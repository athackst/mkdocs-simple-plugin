<!-- md-ignore -->
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
#
# Similarly, you may want to have to have a custom extraction even for a
# standard file pattern, or for one particular file; the `drone.yml` pattern
# could for example extract development documentation from a Drone yml file.
# Note this latter pattern takes advantage of the fact that you can have just
# a single top-level block of parameters in an `extract:` section.
site_name: ok-mkdocs-custom-extract
plugins:
  - simple:
      semiliterate:
        - pattern: '\.litcoffee'
          extract:
            - {stop: '^\s{4,}\S'}  # No start, so active from beginning
            - {start: '# DOCPAGE', stop: '^\s{4,}\S'}
        - pattern: 'drone.yml'
          destination: 'drone_develop.md'
          extract:
            start: '### develop'
            stop: '^\s*###'
            replace: ['^# (.*\s*)$', '^\s*-(.*\s*)$']
```
## Input

```
ok-mkdocs-custom-extract/
├── drone.yml
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
├── drone_develop/
│   └── index.html
├── fibo/
│   └── index.html
└── index.html
```


<div class="admonition quote">
<p class="admonition-title">drone_develop</p>
<h2 id="developing">Developing</h2>
<h1 id="_1"></h1>
<p>You can clone the repository with</p>
<pre><code>git clone https://this_is_a_dummy_url
</code></pre>
<p>You can build the distribution with</p>
<pre><code> pip install build
 python -m build .
</code></pre>
<p>That will produce a <code>.whl</code> file in the <code>dist</code> subdirectory.</p></div>

<div class="admonition quote">
<p class="admonition-title">fibo</p>
<p>This paragraph is here to make sure the extraction starts immediately.</p>
<h1 id="coffee-fibonacci">Coffee Fibonacci</h1>
<p>Although trite, this is an example of the sum recurrence.</p>
<h2 id="complexity">Complexity</h2>
<p>This note about complexity will appear in the doc page.</p></div>
