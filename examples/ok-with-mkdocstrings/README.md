<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Extract docs with mkdocstrings

## mkdocs.yml

```yaml
# You can even use this with other plugins, like 
# [mkdocstrings](https://pypi.org/project/mkdocstrings/), to achieve advanced 
# configurations.
site_name: ok-with-mkdocstrings
plugins:
  - simple
  - mkdocstrings:
      handlers:
        python:
          paths: [examples/ok-with-mkdocstrings, .]
```
## Input

```
ok-with-mkdocstrings/
├── example.md
├── mkdocs.yml
├── module.py
└── README.md
```


**module.py**
```.py
{% raw %}
"""md

## Python Version

You can put _markdown_ in triple-quoted strings in Python.

You can even combine it with mkdocstrings to automatically generate your source
documentation!

::: module.main
    handler: python
    options:
        show_root_heading: true
        show_source: false
        heading_level: 3
"""


def main():
    """Test function which takes no parameters.

    It says "Hello, world!"
    """
    print("Hello, world!")
    return 0

{% endraw %}
```


## Output

```
site/
├── example/
│   └── index.html
├── index.html
├── module/
│   └── index.html
└── objects.inv
```


<div class="admonition quote">
<p class="admonition-title">module</p>
<h2 id="python-version">Python Version</h2>
<p>You can put <em>markdown</em> in triple-quoted strings in Python.</p>
<p>You can even combine it with mkdocstrings to automatically generate your source
documentation!</p>


  <div class="doc doc-object doc-function">



<h3 id="module.main" class="doc doc-heading">
<code class="highlight language-python"><span class="n">module</span><span class="o">.</span><span class="n">main</span><span class="p">()</span></code>


</h3>

    <div class="doc doc-contents first">

      <p>Test function which takes no parameters.</p>
<p>It says "Hello, world!"</p>

    </div>

  </div></div>
