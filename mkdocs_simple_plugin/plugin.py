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
import tempfile
import time
from typing import Callable, Literal

import yaml
from mkdocs import config as mkdocs_config
from mkdocs import utils
from mkdocs.config import config_options
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files

from mkdocs_simple_plugin.simple import Simple


class SimplePlugin(BasePlugin):
    """SimplePlugin adds documentation throughout your repo to a mkdocs wiki."""

    # md file=config_scheme.snippet
    config_scheme = (
        # ### include_folders (renamed)
        #
        # Renamed [folders](#folders)
        ('include_folders', config_options.Deprecated(
            moved_to="folders", removed=False)),
        #
        # ### folders
        #
        # Directories whose name matches a glob pattern in this list will be
        # searched for documentation
        ('folders', config_options.Type(list, default=['*'])),
        #
        # ### ignore_folders (renamed)
        #
        # Renamed [ignore](#ignore)
        ('ignore_folders', config_options.Deprecated(
            moved_to="ignore", removed=False)),
        #
        # ### ignore
        #
        # Directories whose name matches a glob pattern in this list will NOT be
        # searched for documentation.
        ('ignore', config_options.Type(
            list,
            default=[
                "venv",
                ".cache/**",
                ".devcontainer/**",
                ".github/**",
                ".vscode/**",
                "**/__pycache__/**",
                ".git/**",
                "*.egg-info",
            ])),
        #
        # ### ignore_hidden (deprecated)
        #
        # Hidden directories will not be searched if this is true.
        ('ignore_hidden', config_options.Deprecated(
            moved_to=None,
            message="Common ignore files have been added to 'ignore' instead",
            removed=False)),
        #
        # ### merge_docs_dir
        #
        # If true, the contents of the docs directory (if any) will be merged
        # at the same level as all other documentation.
        # Otherwise, the docs directory will be retained as a subdirectory in
        # the result.
        ('merge_docs_dir', config_options.Type(bool, default=True)),
        #
        # ### build_docs_dir (renamed)
        #
        # Renamed [build_dir](#build_dir)
        ('build_docs_dir', config_options.Deprecated(
            moved_to="build_dir", removed=False)),
        #
        # ### build_dir
        #
        # If set, the directory where docs will be collated to be build.
        # Otherwise, the build docs directory will be a temporary directory.
        ('build_dir', config_options.Type(str, default='')),
        #
        # #### copy
        #
        # If set, docs will be copied to the build_docs_dir.
        # Otherwise, files will be used in place.
        ('copy', config_options.Type(bool, default=False)),
        #
        # ### include_extensions (renamed)
        #
        # Renamed [include](#include)
        ('include_extensions', config_options.Deprecated(
            moved_to="include", message="", removed=False)),
        #
        # ### include
        #
        # Any file in the searched directories whose name contains a string in
        # this list will simply be copied to the generated documentation.
        ('include',
            config_options.Type(
                list,
                default=[
                    "*.bmp", "*.tif", "*.tiff", "*.gif", "*.svg", "*.jpeg",
                    "*.jpg", "*.jif", "*.jiff", "*.jp2", "*.jpx", "*.j2k",
                    "*.j2c", "*.fpx", "*.pcd", "*.png", "*.pdf", "CNAME",
                    "*.snippet", ".pages"
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
        # Create a temporary build directory, and set some options to serve it
        # PY2 returns a byte string by default. The Unicode prefix ensures a
        # Unicode string is returned. And it makes MkDocs temp dirs easier to
        # identify.
        self.tmp_build_dir = tempfile.mkdtemp(prefix="mkdocs_simple_")
        self.paths = None
        self.dirty = False
        self.last_build_time = None

    def on_startup(self,
                   *,
                   command: Literal['build',
                                    'gh-deploy',
                                    'serve'],
                   dirty: bool):
        """Configure the plugin on startup."""
        self.dirty = dirty

    def on_config(self, config: MkDocsConfig):
        """Update configuration to use a temporary build directory."""
        # Save the config for documentation
        default_config = dict((name, config_option.default)
                              for name, config_option in self.config_scheme)
        config['mkdocs_simple_config'] = yaml.dump(
            default_config,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            encoding=None)

        # Read previous config first so updates don't get overwritten
        config_site_dir = get_config_site_dir(config.config_file_path)

        # If the build_dir isn't set by the user,
        # set it to one of the following locations:
        if not self.config['build_dir']:
            if self.config['merge_docs_dir']:
                # the build_dir to the docs_dir if merging
                self.config['build_dir'] = config['docs_dir']
            else:
                # or a temp directory
                self.config['build_dir'] = self.tmp_build_dir

        utils.log.info(
            "mkdocs-simple-plugin: build_dir: %s",
            self.config['build_dir'])

        # Create build directory
        os.makedirs(self.config['build_dir'], exist_ok=True)
        # Save original docs directory location
        self.orig_docs_dir = config['docs_dir']
        # Update the docs_dir with our temporary one if not merging
        if not self.config['merge_docs_dir']:
            config['docs_dir'] = self.config['build_dir']
        # Add all markdown extensions to include list
        self.config['include'] = list(utils.markdown_extensions) + \
            self.config['include']

        # Always ignore the output paths
        self.config["ignore_paths"] = [
            os.path.abspath(config_site_dir),
            os.path.abspath(config['site_dir']),
            os.path.abspath(self.config['build_dir'])]
        if self.config['merge_docs_dir']:
            self.config["ignore_paths"].append(
                os.path.abspath(config['docs_dir']))
        return config

    def on_files(self, files: Files, /, *,
                 config: MkDocsConfig):
        """Update files based on plugin settings."""
        # Configure simple
        simple = Simple(**self.config)

        # Save paths to add to watch if serving
        do_copy = self.config["copy"]
        self.paths = simple.build_docs(
            self.dirty, self.last_build_time, do_copy)
        self.last_build_time = time.time()

        if not self.config["merge_docs_dir"]:
            # If not merging, remove files that are from the docs dir
            abs_docs_dir = os.path.abspath(config['docs_dir'])
            for _, file in files.src_uris.items():
                if file.abs_src_path.startswith(abs_docs_dir):
                    files.remove(file)

        for path in self.paths:
            file = File(
                src_dir=os.path.abspath(path.output_root),
                path=path.output_relpath,
                dest_dir=config.site_dir,
                use_directory_urls=config["use_directory_urls"]
            )
            file.generated_by = "mkdocs_simple_plugin"
            if file.src_uri in files.src_uris:
                files.remove(file)
            files.append(file)
        return files

    def on_serve(self, server: LiveReloadServer, /, *, config: MkDocsConfig,
                 builder: Callable):
        """Add files to watch server."""
        # don't watch the build directory
        # pylint: disable=protected-access
        if self.config["build_dir"] in server._watched_paths:
            server.unwatch(self.config["build_dir"])

        # watch all the doc files
        for path in self.paths:
            server.watch(path.input_path)

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
