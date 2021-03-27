<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Extract docs from source

## mkdocs.yml

```yaml
# This examples shows how you can extract markdown from a source file.
site_name: project
plugins:
  - simple
```
## Input

```
ok-source-extract/
├── main.c
├── mkdocs.yml
├── module.py
└── README.md
```


**main.c**
```.c
{% raw %}
#include <stdio.h>

/** md
## Detailed documentation

### block comments

block comments are added with `/** md` and conclude with `**\/` tags.
**/

// md
// ### line comments
// 
// line comments are added with `// md` and conclude with `// end md` tags
// end md
int main() {
  printf("Hello, world!");
  return 0;
}

{% endraw %}
```

**module.py**
```.py
{% raw %}
"""md

## Python Version

You can put _markdown_ in triple-quoted strings in Python.
"""

# md
# ### inline comments
#
# It works in inline comments. The start and end markers must be on their own
# lines.
# /md


def main():
    # noqa: D207
    """<md>Main test.

### docstrings

It works in docstrings. The start and end quotes must be on their own lines.
Drawback: `simple` does not remove leading whitespace.
    """
    print("Hello, world!")
    return 0

{% endraw %}
```


## Output

```
site/
├── index.html
├── main/
│   └── index.html
└── module/
    └── index.html
```


<div class="admonition quote">
<p class="admonition-title">main</p>
   <h2 id="detailed-documentation">Detailed documentation</h2>
   <h3 id="block-comments">block comments</h3>
   <p>block comments are added with <code>/** md</code> and conclude with <code>**\/</code> tags.</p>
   <h3 id="line-comments">line comments</h3>
   <p>line comments are added with <code>// md</code> and conclude with <code>// end md</code> tags</p></div>

<div class="admonition quote">
<p class="admonition-title">module</p>
   <h2 id="python-version">Python Version</h2>
   <p>You can put <em>markdown</em> in triple-quoted strings in Python.</p>
   <h3 id="inline-comments">inline comments</h3>
   <p>It works in inline comments. The start and end markers must be on their own
   lines.</p>
   <h3 id="docstrings">docstrings</h3>
   <p>It works in docstrings. The start and end quotes must be on their own lines.
   Drawback: <code>simple</code> does not remove leading whitespace.</p></div>
