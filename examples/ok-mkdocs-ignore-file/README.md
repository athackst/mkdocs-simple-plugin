<!-- md-ignore -->
<!-- DO NOT EDIT! This file is auto-generated from README.md.ninja -->
# Ignore a file

## mkdocs.yml

```yaml
# This tests if the site directory is ignored in both build and serve.
site_name: ok-mkdocs-ignore-file
plugins:
- simple:
```
## Input

```
ok-mkdocs-ignore-file/
├── hello_world.cpp
├── mkdocs.yml
├── README.md
└── test.md
```


**hello_world.cpp**
```.cpp
{% raw %}
/** md-ignore

# Ignore me

Ignore everything beyond the first line since it contains md-ignore.
**/

#include <iostream>

int main() {
  /** md
  # Hello world
  
  This is the main function for hello world.
  It outputs "Hello World!" to the screen.
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
└── test/
    └── index.html
```

