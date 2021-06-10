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

## Settings

Create a `mkdocs.yml` file in the root of your directory and add the `simple`
plugin to its plugin list.

```yaml
site_name: "My site"
plugins:
- search:
- simple:
```

### Defaults

```yaml
{{ config.mkdocs_simple_config }}
```

!!!Note
    If you add your own settings but want to also use any of these, you
    must reiterate the settings you want in your `mkdocs.yml` file.


### Example usage (defaults)

{% include "mkdocs_simple_plugin/example.snippet" %}

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
import os
import shutil
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
        # Directories whose name matches a glob pattern in this list will be
        # searched for documentation
        ('include_folders', config_options.Type(list, default=['*'])),

        # ### ignore_folders
        # Directories whose name matches a glob pattern in this list will NOT be
        # searched for documentation.
        ('ignore_folders', config_options.Type(list, default=[])),

        # ### ignore_hidden
        # Hidden directories will not be searched if this is true.
        ('ignore_hidden', config_options.Type(bool, default=True)),

        # ### merge_docs_dir
        # If true, the contents of the docs directory (if any) will be merged
        # at the same level as all other documentation.
        # Otherwise, the docs directory will be retained as a subdirectory in
        # the result.
        ('merge_docs_dir', config_options.Type(bool, default=True)),

        # ### build_docs_dir
        # If set, the directory where docs will be coallated to be build.
        # Otherwise, the build docs directory will be a temporary directory.
        ('build_docs_dir', config_options.Type(str, default='')),

        # ### include_extensions
        # Any file in the searched directories whose name contains a string in
        # this list will simply be copied to the generated documentation.
        ('include_extensions',
            config_options.Type(
                list,
                default=[
                    ".bmp", ".tif", ".tiff", ".gif", ".svg", ".jpeg",
                    ".jpg", ".jif", ".jfif", ".jp2", ".jpx", ".j2k",
                    ".j2c", ".fpx", ".pcd", ".png", ".pdf", "CNAME",
                    ".snippet", ".pages"
                ])),

        # ### semiliterate
        # The semiliterate settings allows the extraction of markdown from
        # inside source files.
        # It is defined as a list of blocks of settings for different
        # filename patterns (typically matching filename extensions).
        # All regular expression parameters use ordinary Python `re` syntax.
        #
        #  {% include "mkdocs_simple_plugin/semiliterate.snippet" %}
        # /md

        # md file="example.snippet"
        ('semiliterate',
            config_options.Type(
                list,
                default=[
                    {
                        # #### Python
                        'pattern': r'\.py$',
                        'extract': [
                            {
                                #
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
                            }
                        ]
                    },
                    {
                        # #### C, C++, and Javascript
                        'pattern': r'\.(cpp|cc?|hh?|hpp|js|css)$',
                        'extract': [
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
                            }
                        ]

                    },
                    {
                        # #### YAML, Dockerfiles, and shell scripts
                        'pattern': r'Dockerfile$|\.(dockerfile|ya?ml|sh)$',
                        'extract': [{
                            # line-comment blocks starting with
                            # `# md` and ending with `# /md`,
                            'start': r'^\s*#+\W?md\b',
                            'stop': r'#\s\/md\s*$',
                            # stripping leading spaces and `#`
                            'replace': [r'^\s*#?\s?(.*\n?)$'],
                            #
                            # ```yaml
                            # # md
                            # # This is a documentation comment.
                            # # /md
                            # ```
                            #
                        }]
                    },
                    {
                        # #### HTML and xml
                        'pattern': r'\.(html?|xml)$',
                        'extract': [{
                            # line-comment blocks starting with
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
                        }]
                    },
                ]))
    )
    # /md

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
        self.build_docs_dir = self.config['build_docs_dir']
        if not self.build_docs_dir:
            self.build_docs_dir = tempfile.mkdtemp(
                prefix="mkdocs_simple_{}".format(
                    os.path.basename(os.path.dirname(config.config_file_path))))
        utils.log.info("mkdocs-simple-plugin: build_docs_dir: {}".format(
            self.build_docs_dir))
        # Clean out build folder on config
        shutil.rmtree(self.build_docs_dir, ignore_errors=True)
        os.makedirs(self.build_docs_dir, exist_ok=True)
        # Save original docs directory location
        self.orig_docs_dir = config['docs_dir']
        # Update the docs_dir with our temporary one
        config['docs_dir'] = self.build_docs_dir
        self.include_folders = self.config['include_folders']
        self.ignore_folders = self.config['ignore_folders']
        self.ignore_hidden = self.config['ignore_hidden']
        self.include_extensions = utils.markdown_extensions + \
            self.config['include_extensions']
        self.merge_docs_dir = self.config['merge_docs_dir']
        self.semiliterate = []
        for item in self.config['semiliterate']:
            self.semiliterate.append(Semiliterate(**item))

        # Always ignore the output paths
        self.ignore_paths = [self.get_config_site_dir(config.config_file_path),
                             config['site_dir'],
                             self.build_docs_dir]
        return config

    def on_pre_build(self, config, **kwargs):
        """Build documentation directory with files according to settings."""
        # Copy contents of docs directory if merging
        if self.merge_docs_dir and os.path.exists(self.orig_docs_dir):
            self.copy_docs_directory(self.orig_docs_dir, self.build_docs_dir)
            self.ignore_paths += [self.orig_docs_dir]
        # Copy all of the valid doc files into build_docs_dir
        self.paths = self.build_docs()

    def on_serve(self, server, config, **kwargs):
        """Add files to watch server."""
        # still watch the original docs/ directory
        if os.path.exists(self.orig_docs_dir):
            server.watch(self.orig_docs_dir)

        # watch all the doc files
        for path in self.paths:
            server.watch(path)

        return server

    def in_search_directory(self, directory, root):
        """Check if directory should be searched."""
        if self.ignore_hidden and (directory[0] == "."
                                   or directory == "__pycache__"):
            return False
        path = os.path.join(root, directory)
        if os.path.abspath(path) in self.ignore_paths:
            return False
        if any(fnmatch.fnmatch(path[2:], filter)
                for filter in self.ignore_folders):
            return False
        return True

    def in_include_directory(self, directory):
        """Check if directory in include list."""
        return any(fnmatch.fnmatch(directory, filter)
                   for filter in self.include_folders)

    def in_extensions(self, file):
        """Check if file is in include extensions."""
        return any(extension in file for extension in self.include_extensions)

    def get_config_site_dir(self, config_file_path):
        """Get configuration directory from mkdocs.yml file.

        This is needed in the case you are running mkdocs serve, which
        overwrites the path with a temporary one.
        """
        orig_config = mkdocs_config.load_config(config_file_path)
        utils.log.debug(
            "mkdocs-simple-plugin: loading file: {}".format(config_file_path))

        utils.log.debug(
            "mkdocs-simple-plugin: User config site_dir: {}".format(
                orig_config.data['site_dir']))
        return orig_config.data['site_dir']

    def build_docs(self):
        """Build the docs directory from workspace files."""
        paths = []
        for root, directories, files in os.walk("."):
            if self.in_include_directory(root):
                document_root = self.build_docs_dir + root[1:]
                for f in files:
                    copied = self.copy_file(root, f, document_root)
                    extracted = self.extract_from(root, f, document_root)
                    if copied or extracted:
                        paths.append(os.path.join(root, f))
            directories[:] = [d for d in directories
                              if self.in_search_directory(d, root)]
        return paths

    def copy_file(self, from_directory, name, destination_directory):
        """Copy file with the same name to a new directory.

        Returns true if file copied.
        """
        original = os.path.join(from_directory, name)
        if self.in_extensions(name):
            new_file = os.path.join(destination_directory, name)
            try:
                os.makedirs(destination_directory, exist_ok=True)
                shutil.copy(original, new_file)
                utils.log.debug("mkdocs-simple-plugin: {} --> {}".format(
                    original, new_file))
                return True
            except Exception as e:
                utils.log.warn(
                    "mkdocs-simple-plugin: error! {}.. skipping {}".format(
                        e, original))
        return False

    def extract_from(self, from_directory, name, destination_directory):
        """Extract content from file into destination.

        Returns the name of the file extracted if extractable.
        """
        extracted = False
        for item in self.semiliterate:
            if item.try_extraction(from_directory, name, destination_directory):
                extracted = True

        return extracted

    def copy_docs_directory(self, root_source_directory,
                            root_destination_directory):
        """Copy all files from source to destination directory."""
        if sys.version_info >= (3, 8):
            # pylint: disable=unexpected-keyword-arg
            shutil.copytree(root_source_directory,
                            root_destination_directory,
                            dirs_exist_ok=True)
            utils.log.debug("mkdocs-simple-plugin: {}/* --> {}/*".format(
                root_source_directory, root_destination_directory))
        else:
            for source_directory, _, files in os.walk(root_source_directory):
                destination_directory = source_directory.replace(
                    root_source_directory, root_destination_directory, 1)
                os.makedirs(destination_directory, exist_ok=True)
                for file_ in files:
                    source_file = os.path.join(source_directory, file_)
                    destination_file = os.path.join(destination_directory,
                                                    file_)
                    if os.path.exists(destination_file):
                        os.remove(destination_file)
                    shutil.copy(source_file, destination_directory)
                    utils.log.debug(
                        "mkdocs-simple-plugin: {}/* --> {}/*".format(
                            source_file, destination_file))
