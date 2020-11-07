# MkDocs Simple Plugin

A plugin to the mkdocs package that builds a documentation website from .md files interspersed with in your code

## Installation

Install the plugin with pip.

```bash
pip install mkdocs-simple-plugin
```

_Python 3.x, 3.5, 3.6, 3.7, 3.8, 3.9 supported._

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
      include_extensions: [".tif", ".tiff", ".gif", ".jpeg", ".jpg", ".jif", ".jfif",
            ".jp2", ".jpx", ".j2k", ".j2c", ".fpx", ".pcd", ".png", ".pdf", "CNAME"]
      # Optional setting to merge the docs directory with other documentation
      merge_docs_dir: True
```

### Build

Then, you can build the mkdocs from the command line.

```bash
mkdocs build
```

### Run a local server

One of the best parts of mkdocs is it's ability to serve (and update!) your documentation site locally.

```bash
mkdocs serve
```
