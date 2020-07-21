# Reference

This python package provides the following objects

## mkdocs-simple-plugin

A plugin to the mkdocs package that builds a documentation website from .md files interspersed with in your code

Note: Files in the `docs_dir` (by default `docs`) will be merged with any other documentation in your repository.

### Plugin usage

Create a `mkdocs.yml` file in the root of your directory and add this plugin to it's plugin list.

```yaml
site_name: your_site_name
plugins:
  - simple:
      # Optional setting to only include specific folders
      include_folders: ["*"]
      # Optional setting to ignore specific folders
      ignore_folders: [""]
      # Optional setting to specify if hidden folders should be ignored
      ignore_hidden: True
      # Optional setting to specify other extensions besides md files to be copied
      include_extensions: [""]
```

## mkdocs_simple_gen

A program that will automatically create a `mkdocs.yml` configuration file (only if needed) and optionally install dependencies, build, and serve the site.

### Command line options

See `--help`

```txt
Usage: mkdocs_simple_gen [OPTIONS]

Options:
  --build / --no-build      build the site using mkdocs build
  --install / --no-install  install required packages listed in
                            requirements.txt

  --serve / --no-serve      serve the site locally
  --dev-addr TEXT           Local server address
  --help                    Show this message and exit.
```

default flags:

```bash
mkdocs_simple_gen --build --no-install --no-serve
```

Flags are processed in the following order:

1. install -> to install needed packages from requirements.txt for building
2. build -> build the website
3. serve -> serve the site locally
