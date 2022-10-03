"""md

# Mkdocs Simple Plugin

A plugin for MkDocs that builds a documentation website from markdown content
interspersed within your code, in markdown files or in block comments in your
source files.

`simple` will search your project directory tree for documentation. By default,
Markdown files and graphics files will be copied to your documentation site.
Source files will also be searched for markdown embedded in minimally-structured
comment blocks; these will be extracted into additional markdown files included
in the documentation site.

## Installation

Install the plugin with pip.

```bash
pip install mkdocs-simple-plugin
```

{% include "versions.snippet" %}

## Usage

Create a `mkdocs.yml` file in the root of your directory and add the `simple`
plugin to its plugin list.

```yaml
site_name: "My site"
plugins:
- search:
- simple:
```

### Example usage (defaults)

{% include "mkdocs_simple_plugin/example.snippet" %}

### Inline parameters

Inline parameters configure a block's extraction.

{% include "mkdocs_simple_plugin/inline_params.snippet" %}

### Ignoring files

You can add a `.mkdocsignore` file to ignore a directory or files by glob
pattern.

See [example mkdocsignore usage](../examples/ok-mkdocsignore/README.md)

## Default settings

Below are the default settings of the plugin.

```yaml
{{ config.mkdocs_simple_config }}
```

!!!Note
    If you add your own settings but want to also use any of these, you
    must reiterate the settings you want in your `mkdocs.yml` file.

## Configuration scheme

{% include "mkdocs_simple_plugin/config_scheme.snippet" %}

## Build

You can build mkdocs from the command line using the standard command

```bash
mkdocs build
```

or you can generate and build at the same time [see generator](generator.md).

## Run a local server

One of the best parts of mkdocs is the ability to serve (and update!) your
documentation site locally.

```bash
mkdocs serve
```

"""
import os
import shutil
import tempfile
import yaml


from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs import config as mkdocs_config
from mkdocs import utils

from mkdocs_simple_plugin.simple import Simple


class SimplePlugin(BasePlugin):
    """SimplePlugin adds documentation throughout your repo to a mkdocs wiki."""

    # md file=config_scheme.snippet
    config_scheme = (
        # ### include_folders
        #
        # Directories whose name matches a glob pattern in this list will be
        # searched for documentation
        ('include_folders', config_options.Type(list, default=['*'])),
        #
        # ### ignore_folders
        #
        # Directories whose name matches a glob pattern in this list will NOT be
        # searched for documentation.
        ('ignore_folders', config_options.Type(list, default=[])),
        #
        # ### ignore_hidden
        #
        # Hidden directories will not be searched if this is true.
        ('ignore_hidden', config_options.Type(bool, default=True)),
        #
        # ### merge_docs_dir
        #
        # If true, the contents of the docs directory (if any) will be merged
        # at the same level as all other documentation.
        # Otherwise, the docs directory will be retained as a subdirectory in
        # the result.
        ('merge_docs_dir', config_options.Type(bool, default=True)),
        #
        # ### build_docs_dir
        #
        # If set, the directory where docs will be collated to be build.
        # Otherwise, the build docs directory will be a temporary directory.
        ('build_docs_dir', config_options.Type(str, default='')),
        #
        # ### include_extensions
        #
        # Any file in the searched directories whose name contains a string in
        # this list will simply be copied to the generated documentation.
        ('include_extensions',
            config_options.Type(
                list,
                default=[
                    ".bmp", ".tif", ".tiff", ".gif", ".svg", ".jpeg",
                    ".jpg", ".jif", ".jiff", ".jp2", ".jpx", ".j2k",
                    ".j2c", ".fpx", ".pcd", ".png", ".pdf", "CNAME",
                    ".snippet", ".pages"
                ])),
        #
        # ### semiliterate
        #
        # The semiliterate settings allows the extraction of markdown from
        # inside source files.
        # It is defined as a list of blocks of settings for different
        # filename patterns (typically matching filename extensions).
        # All regular expression parameters use ordinary Python `re` syntax.
        #
        # {% include "mkdocs_simple_plugin/Semiliterate.snippet" %}
        #
        # {% include "mkdocs_simple_plugin/ExtractionPattern.snippet" %}
        # /md


        ('semiliterate',
            config_options.Type(
                list,
                default=[
                    {
                        'pattern': r'^LICENSE$',
                    },
                    {
                        'pattern': r'.*',
                        'terminate': r'^\W*md-ignore',
                        'extract': [
                            {
                                # md file="example.snippet"
                                # block comments starting with: `"""md`
                                'start': r'^\s*"""\W?md\b',
                                'stop': r'^\s*"""\s*$',
                                #
                                # ```python
                                # """md
                                # This is a documentation comment.
                                # """
                                # ```
                                #
                            },
                            {
                                # line comments starting with:
                                # `# md` and ending with `# /md`,
                                'start': r'^\s*#+\W?md\b',
                                'stop': r'^\s*#\s?\/md\s*$',
                                # stripping leading spaces and `#``,
                                # and only capturing comment lines.
                                'replace': [r'^\s*# ?(.*\n?)$', r'^.*$'],
                                #
                                # ```python
                                # # md
                                # # This is a documentation comment.
                                # # /md
                                # ```
                                #
                            },
                            {
                                # block comments starting with: `/** md`
                                'start': r'^\s*/\*+\W?md\b',
                                'stop': r'^\s*\*\*/\s*$',
                                #
                                # ```c
                                # /** md
                                # This is a documentation comment.
                                # **/
                                # ```
                                #
                            },
                            {
                                # in line comments starting with
                                # `// md`, ending with `// end md`,
                                'start': r'^\s*\/\/+\W?md\b',
                                'stop': r'^\s*\/\/\send\smd\s*$',
                                # stripping leading spaces and `//`,
                                # and only capturing comment lines.
                                'replace': [r'^\s*\/\/\s?(.*\n?)$', r'^.*$'],
                                #
                                # ```c
                                # // md
                                # // This is a documentation comment.
                                # // end md
                                # ```
                                #
                            },
                            {
                                # block comments starting with
                                # `<!-- md` and ending with `-->`
                                'start': r'<!--\W?md\b',
                                'stop': r'-->\s*$',
                                #
                                # ```xml
                                # <!-- md
                                # This is a documentation comment.
                                # -->
                                # ```
                                #
                            }
                        ]
                    }
                ]))
    )
    # /md

    def __init__(self):
        """Set up internal variables."""
        self.orig_docs_dir = None
        self.paths = None

    def on_config(self, config, **kwargs):
        """Update configuration to use a temporary build directory."""
        default_config = dict((name, config_option.default)
                              for name, config_option in self.config_scheme)
        config['mkdocs_simple_config'] = yaml.dump(
            default_config,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            encoding=None)

        # Create a temporary build directory, and set some options to serve it
        # PY2 returns a byte string by default. The Unicode prefix ensures a
        # Unicode string is returned. And it makes MkDocs temp dirs easier to
        # identify.
        build_docs_dir = self.config['build_docs_dir']
        if not build_docs_dir:
            build_docs_dir = tempfile.mkdtemp(
                prefix="mkdocs_simple_" +
                os.path.basename(
                    os.path.dirname(
                        config.config_file_path)))
        utils.log.info(
            "mkdocs-simple-plugin: build_docs_dir: %s",
            build_docs_dir)
        self.config['build_docs_dir'] = build_docs_dir
        # Clean out build folder on config
        shutil.rmtree(build_docs_dir, ignore_errors=True)
        os.makedirs(build_docs_dir, exist_ok=True)
        # Save original docs directory location
        self.orig_docs_dir = config['docs_dir']
        # Update the docs_dir with our temporary one
        config['docs_dir'] = build_docs_dir
        # Add all markdown extensions to include list
        self.config['include_extensions'] = list(utils.markdown_extensions) + \
            self.config['include_extensions']

        # Always ignore the output paths
        self.config["ignore_paths"] = [
            get_config_site_dir(config.config_file_path),
            config['site_dir'],
            self.config['build_docs_dir']]
        return config

    def on_pre_build(self, *, config):
        """Build documentation directory with files according to settings."""
        # Configure simple
        simple = Simple(**self.config)

        # Merge docs
        if self.config["merge_docs_dir"]:
            simple.merge_docs(self.orig_docs_dir)
        # Copy all of the valid doc files into build_docs_dir
        self.paths = simple.build_docs()

    def on_serve(self, server, *, config, builder):
        """Add files to watch server."""
        # watch the original docs/ directory
        if os.path.exists(self.orig_docs_dir):
            server.watch(self.orig_docs_dir)

        # watch all the doc files
        for path in self.paths:
            server.watch(path)

        return server


def get_config_site_dir(config_file_path: str) -> str:
    """Get configuration directory from mkdocs.yml file.

    This is needed in the case you are running mkdocs serve, which
    overwrites the path with a temporary one.
    """
    orig_config = mkdocs_config.load_config(config_file_path)
    utils.log.debug(
        "mkdocs-simple-plugin: loading file: %s", config_file_path)

    utils.log.debug(
        "mkdocs-simple-plugin: User config site_dir: %s",
        orig_config.data['site_dir'])
    return orig_config.data['site_dir']
