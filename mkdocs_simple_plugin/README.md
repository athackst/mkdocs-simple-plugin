# Package Guide

## Prerequisites

{% include "setup.snippet" %}


## Building

{% include "build.snippet" %}

## Testing
 
{% include "tests/test.snippet" %}

## VSCode

Included in this package is a VSCode workspace and development container.  See [how I develop with VSCode and Docker](https://allisonthackston.com/articles/docker-development.html) and [how I use VSCode tasks](https://allisonthackston.com/articles/vscode-tasks.html).

## Packaging

[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

The project uses Hatch to build and package the plugin

### Build the package

```bash
hatch build
```

### Publish the package

```bash
hatch publish
```
