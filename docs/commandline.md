# MkDocs Simple Gen

A program that will automatically create a `mkdocs.yml` configuration file (only if needed) and optionally install dependencies, build, and serve the site.

## Installation

Install the plugin with pip.

```bash
pip install mkdocs-simple-plugin
```

_Python 3.x, 3.5, 3.6, 3.7, 3.8 supported._


### Command line options

See `--help`

```txt
Usage: mkdocs_simple_gen [OPTIONS]

Options:
  --build / --no-build      build the site using mkdocs build
  --help                    Show this message and exit.
```

default flags:

```bash
mkdocs_simple_gen --build
```

### Run a local server

One of the best parts of mkdocs is it's ability to serve (and update!) your documentation site locally.

```bash
mkdocs serve
```
