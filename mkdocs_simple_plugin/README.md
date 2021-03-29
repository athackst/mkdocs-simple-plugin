# Developing

## Prerequisites

You will need to have [MKDocs](https://www.mkdocs.org/) installed on your system.
I recommend installing it via pip to get the latest version.

```bash
sudo apt-get install python-pip
pip install --upgrade pip --user
pip install mkdocs --user
```
## Local install

Install the package locally with

```bash
pip install -e .
```

## Testing

{% include "tests/testing.snippet" %}

## VSCode

Included in this package is a VSCode workspace and development container.  See [how I develop with VSCode and Docker](https://www.allisonthackston.com/articles/docker_development.html) and [how I use VSCode tasks](https://www.allisonthackston.com/articles/vscode_tasks.html).
