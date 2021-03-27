<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Extract a snippet

## mkdocs.yml

```yaml
# This is example shows to to create a snippet from a file.  For example, you 
# can use a snippet to rerrange contents using inclusion or create a new pages 
# per module.
site_name: project
plugins:
  - simple
```
## Input

```
ok-source-with-snippet/
├── mkdocs.yml
├── module.py
├── README.md
```


**module.py**
```.py
{% raw %}
"""md

## Main file

You can even make snippets as separate files.

"""

# md file=snippet.md
#
# ## Snippet
#
# This is a snippet from module.py.
# /md

"""<md file="snippet2.md">Another one.

## Snippet2

This is another snippet from module.py
"""


def main():
    """Main function which prints "Hello, World!"""
    print("Hello, world!")
    return 0

{% endraw %}
```


## Output

```
site/
├── index.html
├── module/
│   └── index.html
├── snippet/
│   └── index.html
└── snippet2/
    └── index.html
```


<div class="admonition quote">
<p class="admonition-title">module</p>
<h2 id="main-file">Main file</h2>
<p>You can even make snippets as separate files.</p></div>

<div class="admonition quote">
<p class="admonition-title">snippet</p>
<h2 id="snippet">Snippet</h2>
<p>This is a snippet from module.py.</p></div>

<div class="admonition quote">
<p class="admonition-title">snippet2</p>
<h2 id="snippet2">Snippet2</h2>
<p>This is another snippet from module.py</p></div>
