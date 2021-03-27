<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Extract docs with macros

## mkdocs.yml

```yaml
# You can even use this with other plugins, like 
# [macros](https://pypi.org/project/mkdocs-macros-plugin/) to achieve advanced 
# configurations.
site_name: project
docs_dir: /tmp/mkdocs-simple/ok-with-macros/docs
plugins:
    - search
    - simple:
          include_extensions:
              - ".yml"
    - macros:
          verbose: True
extra:
    test: True
```
## Input

```
ok-with-macros/
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

You can even use macros to inject other markdown here!

For example, here's the config file:

````yaml
{% include 'mkdocs.yml' %}
````
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
├── mkdocs-test.yml
├── mkdocs.yml
└── module/
    └── index.html
```


<div class="admonition quote">
<p class="admonition-title">module</p>
<h2 id="python-version">Python Version</h2>
<p>You can put <em>markdown</em> in triple-quoted strings in Python.</p>
<p>You can even use macros to inject other markdown here!</p>
<p>For example, here's the config file:</p>
<pre><code class="language-yaml">site_name: project
docs_dir: /tmp/mkdocs-simple/ok-with-macros/docs
plugins:
  - search
  - simple:
      include_extensions:
        - .yml
  - macros:
      verbose: true
extra:
  test: true
</code></pre></div>
