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

Then, you can build the mkdocs from the command line.

```bash
mkdocs build
```

## Run a local server

One of the best parts of mkdocs is the ability to serve (and update!) your
documentation site locally.

```bash
mkdocs serve
```

"""
import fnmatch
import glob
import os
import shutil
import stat
import sys
import tempfile
import yaml


from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs import config as mkdocs_config
from mkdocs import utils

from mkdocs_simple_plugin.semiliterate import Semiliterate


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
        self.config['include_extensions'] = utils.markdown_extensions + \
            self.config['include_extensions']

        # Always ignore the output paths
        self.config["ignore_paths"] = [
            get_config_site_dir(config.config_file_path),
            config['site_dir'],
            self.config['build_docs_dir']]
        return config

    def on_pre_build(self, config, **kwargs):
        """Build documentation directory with files according to settings."""
        # Configure simple
        simple = Simple(**self.config)

        # Merge docs
        if self.config["merge_docs_dir"]:
            simple.merge_docs(self.orig_docs_dir)
        # Copy all of the valid doc files into build_docs_dir
        self.paths = simple.build_docs()

    def on_serve(self, server, config, **kwargs):
        """Add files to watch server."""
        # watch the original docs/ directory
        if os.path.exists(self.orig_docs_dir):
            server.watch(self.orig_docs_dir)

        # watch all the doc files
        for path in self.paths:
            server.watch(path)

        return server


class Simple():
    """Mkdocs Simple Plugin"""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            build_docs_dir: str,
            include_folders: list,
            include_extensions: list,
            ignore_folders: list,
            ignore_hidden: bool,
            ignore_paths: list,
            semiliterate: dict,
            **kwargs):
        """Initialize module instance with settings."""
        self.build_dir = build_docs_dir
        self.include_folders = set(include_folders)
        self.include_extensions = set(include_extensions)
        self.ignore_folders = set(ignore_folders)
        self.ignore_hidden = ignore_hidden
        self.hidden_prefix = set([".", "__"])
        self.ignore_paths = set(ignore_paths)
        self.semiliterate = []
        for item in semiliterate:
            self.semiliterate.append(Semiliterate(**item))

    def is_hidden(self, filepath):
        """Return true if filepath is hidden."""
        def has_hidden_attribute(filepath):
            """Returns true if hidden attribute is set."""
            try:
                return bool(os.stat(filepath).st_file_attributes &
                            stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, AssertionError):
                return False

        def has_hidden_prefix(filepath):
            name = os.path.basename(os.path.abspath(filepath))
            return any(name.startswith(pattern)
                       for pattern in self.hidden_prefix)

        return has_hidden_prefix(filepath) or has_hidden_attribute(filepath)

    def is_ignored(self, base_path: str, name: str) -> bool:
        """Check if directory and filename should be ignored."""
        return self.is_path_ignored(os.path.join(base_path, name))

    def is_path_ignored(self, path: str = None) -> bool:
        """Check if path should be ignored."""
        path = os.path.normpath(path)
        base_path = os.path.dirname(path)
        # Check if it's hidden
        if self.ignore_hidden and self.is_hidden(path):
            return True
        # Check if its an internally required ignore path
        if os.path.abspath(path) in self.ignore_paths:
            return True

        # Update ignore patterns from .mkdocsignore file
        mkdocsignore = os.path.join(base_path, ".mkdocsignore")
        if os.path.exists(mkdocsignore):
            ignore_list = []
            with open(mkdocsignore, "r") as txt_file:
                ignore_list = txt_file.read().splitlines()
                # Remove all comment lines
                ignore_list = [x for x in ignore_list if not x.startswith('#')]
            if not ignore_list:
                ignore_list = ["*"]
            self.ignore_folders.update(
                set(os.path.join(base_path, filter) for filter in ignore_list))
        # Check for ignore paths in patterns
        if any(fnmatch.fnmatch(os.path.normpath(path), filter)
                for filter in self.ignore_folders):
            return True
        return False

    def get_included(self) -> list:
        """Get a list of folders and files to include."""
        included = []
        for pattern in self.include_folders:
            included.extend(glob.glob(pattern))
        # Return filtered list of included files
        return [f for f in included if not self.is_path_ignored(f)]

    def in_extensions(self, name: str) -> bool:
        """Check if file is in include extensions."""
        return any(extension in name for extension in self.include_extensions)

    def merge_docs(self, from_dir):
        """Merge docs directory"""
        # Copy contents of docs directory if merging
        if os.path.exists(from_dir):
            copy_directory(from_dir, self.build_dir)
            self.ignore_paths.add(from_dir)

    def build_docs(self) -> list:
        """Build the docs directory from workspace files."""
        paths = []
        included = self.get_included()
        for item in included:
            paths += filter(None, [self._process(item)])
            for root, directories, files in os.walk(item):
                for file in files:
                    path = os.path.join(root, file)
                    paths += filter(None, [self._process(path)])
                directories[:] = [
                    d for d in directories if not self.is_ignored(root, d)]
        return paths

    def _process(self, file) -> str:
        if not os.path.isfile(file):
            return None
        from_dir = os.path.dirname(file)
        name = os.path.basename(file)
        build_prefix = os.path.normpath(os.path.join(self.build_dir, from_dir))

        if (self.try_copy_file(from_dir, name, build_prefix) or
                self.try_extract(from_dir, name, build_prefix)):
            return file
        return None

    def try_copy_file(self, from_dir: str, name: str, to_dir: str) -> bool:
        """Copy file with the same name to a new directory.

        Returns true if file copied.
        """
        original = os.path.join(from_dir, name)
        new_file = os.path.join(to_dir, name)

        if not self.in_extensions(name):
            utils.log.info(
                "mkdocs-simple-plugin: skipping file extension %s", original)
            return False
        if self.is_path_ignored(original):
            utils.log.debug(
                "mkdocs-simple-plugin: ignoring %s", original)
            return False
        try:
            os.makedirs(to_dir, exist_ok=True)
            shutil.copy(original, new_file)
            utils.log.debug("mkdocs-simple-plugin: %s --> %s",
                            original, new_file)
            return True
        except (OSError, IOError, UnicodeDecodeError) as error:
            utils.log.warning(
                "mkdocs-simple-plugin: %s.. skipping %s",
                error, original)
        return False

    def try_extract(self, from_dir: str, name: str, to_dir: str) -> bool:
        """Extract content from file into destination.

        Returns the name of the file extracted if extractable.
        """
        path = os.path.join(from_dir, name)
        if self.is_path_ignored(path):
            utils.log.debug(
                "mkdocs-simple-plugin: ignoring %s", path)
            return False
        extracted = False
        for item in self.semiliterate:
            if item.try_extraction(from_dir, name, to_dir):
                extracted = True

        return extracted


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


def copy_directory(from_dir: str, to_dir: str):
    """Copy all files from source to destination directory."""
    if sys.version_info >= (3, 8):
        # pylint: disable=unexpected-keyword-arg
        shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)
        utils.log.debug("mkdocs-simple-plugin: %s/* --> %s/*",
                        from_dir, to_dir)
    else:
        for source_directory, _, files in os.walk(from_dir):
            destination_directory = source_directory.replace(
                from_dir, to_dir, 1)
            os.makedirs(destination_directory, exist_ok=True)
            for file_ in files:
                source_file = os.path.join(source_directory, file_)
                destination_file = os.path.join(destination_directory,
                                                file_)
                if os.path.exists(destination_file):
                    os.remove(destination_file)
                shutil.copy(source_file, destination_directory)
                utils.log.debug(
                    "mkdocs-simple-plugin: %s/* --> %s/*",
                    source_file, destination_file)
