<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Advanced replacement

## mkdocs.yml

```yaml
# This example shows how to replace lines with regex expressions!
site_name: ok-source-replace
plugins:
  - simple:
      semiliterate:
        - pattern: \.py$
          extract:
            - start: ^\s*"""\W?md\b
              stop: ^\s*"""\s*$
              replace: 
                # replace "foo" with "bar"
                - ["(.*)foo(.*)$", "\\1bar\\2"] 
                # only capture what's after args and replace with parameter prefix
                - ["args:(.*)$","parameters:\\1"] 
                # capture everything after `only_this:`
                - "only_this:(.*)$"
                # drop lines starting with drop 
                - "^drop"
```
## Input

```
ok-source-replace/
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

You can even replace things!

You should see foo replaced by bar in this sentence.

args: This line should start with `parameters`.

blah blah blah only_this: Only this is captured.

drop this line!
"""


def main():
    """Main test."""
    print("Hello, world!")
    return 0

{% endraw %}
```


## Output

```
site/
├── index.html
└── module/
    └── index.html
```


<div class="admonition quote">
<p class="admonition-title">module</p>
<h2 id="python-version">Python Version</h2>
<p>You can put <em>markdown</em> in triple-quoted strings in Python.</p>
<p>You can even replace things!</p>
<p>You should see bar replaced by bar in this sentence.</p>
<p>parameters: This line should start with <code>parameters</code>.</p>
<p>Only this is captured.</p></div>
