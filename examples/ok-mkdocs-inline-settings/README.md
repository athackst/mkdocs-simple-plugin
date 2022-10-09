<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Extract with inline settings

## mkdocs.yml

```yaml
# This is the simplest documentation site you could have.  
# It's just a simple readme.
site_name: ok-mkdocs-inline-settings
plugins:
  - simple
```
## Input

```
ok-mkdocs-inline-settings/
├── hello_world.cpp
├── mkdocs.yml
└── README.md
```


**hello_world.cpp**
```.cpp
{% raw %}
#include <iostream>

int main() {
  /** md file=main.md trim=2 stop="end-here"
  # Hello world
  
  This is the main function for hello world.
  It outputs "Hello World!" to the screen.

  end-here
  This shouldn't show up!
  **/
    std::cout << "Hello World!";
    return 0;
}

{% endraw %}
```


## Output

```
site/
├── index.html
└── main/
    └── index.html
```


<div class="admonition quote">
<p class="admonition-title">main</p>
<h1 id="hello-world">Hello world</h1>
<p>This is the main function for hello world.
It outputs "Hello World!" to the screen.</p></div>
