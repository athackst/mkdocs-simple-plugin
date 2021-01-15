""" md
# MkDocs Simple Plugin

A plugin for MkDocs that builds a documentation website from markdown content
interspersed within your code, in markdown files or in block comments in your
source files.

To summarize its operation briefly, `simple` will search your project directory
tree for documentation. By default, Markdown files and graphics files will be
copied to your documentation site. In addition, source files will be searched
for markdown embedded in minimally-structured comment blocks; such content will
be extracted into additional markdown files included in the documentation site.

## Installation

Install the plugin with pip.

```bash
pip install mkdocs-simple-plugin
```

_Python 3.x, 3.5, 3.6, 3.7, 3.8, 3.9 supported._

## Quick start

### Configuration file

Create a `mkdocs.yml` file in the root of your directory and add the `simple`
plugin to its plugin list.

```yaml
site_name: "My site"
plugins:
- search:
- simple:
```

### Build

Then, you can build the mkdocs from the command line.

```bash
mkdocs build
```

### Run a local server

One of the best parts of mkdocs is the ability to serve (and update!) your
documentation site locally.

```bash
mkdocs serve
```

## Plugin settings

The example YAML below shows all of the configuration parameters for the plugin
and their default values.

```yaml
{{ config.mkdocs_simple_config }}
```

"""
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs import config as mkdocs_config
from mkdocs import utils

import fnmatch
import os
import re
import shutil
import sys
import tempfile
import yaml


class LazyFile:
    """
    Like a file object, but only ever creates the directory and opens the
    file if a non-empty string is written.
    """

    def __init__(self, directory, name):
        self.file_directory = directory
        self.file_name = name
        self.file_object = None

    def write(self, arg):
        if arg == '':
            return
        if self.file_object is None:
            os.makedirs(self.file_directory, exist_ok=True)
            self.file_object = open(
                f"{self.file_directory}/{self.file_name}", 'a+')
        self.file_object.write(arg)

    def close(self):
        if self.file_object is not None:
            self.file_object.close()


class StreamExtract:
    """
    A StreamExtract object copies _input_stream_ to
    _output_stream_, extracting portions of the input_stream as specified
    by the keyword arguments to the constructor as documented for the
    "semiliterate" parameter of the `simple` plugin.
    """

    def __init__(self, input_stream, output_stream,
                 terminate=None, include_root=None, extract={},
                 **ignore_other_kwargs):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.terminate = (terminate is not None) and re.compile(terminate)
        self.include_root = include_root
        self.active_mode = None
        self.modes = []
        for mode in extract if isinstance(extract, list) else [extract]:
            add_mode = {}
            add_mode['stop'] = ('stop' in mode) and re.compile(mode['stop'])
            add_mode['replace'] = []
            for item in mode.get('replace', []):
                if isinstance(item, str):
                    add_mode['replace'].append(re.compile(item))
                else:
                    add_mode['replace'].append((re.compile(item[0]), item[1]))
            if 'start' in mode:
                add_mode['start'] = re.compile(mode['start'])
                self.modes.append(add_mode)
            else:
                self.active_mode = add_mode
        self.wrote_something = False

    def transcribe(self, text):
        self.output_stream.write(text)
        if text:
            self.wrote_something = True

    def check_pattern(self, pattern, line, emit_last=True):
        """ If _pattern_ is not false-y and is contained in _line_,
            returns true (and if the _emit_last_ flag is true,
            emits the last group of the match if any). Otherwise,
            check_pattern does nothing but return false.
        """
        if not pattern:
            return False
        match_object = pattern.search(line)
        if not match_object:
            return False
        if match_object.lastindex and emit_last:
            self.transcribe(match_object[match_object.lastindex])
        return True

    def extract(self):
        """ Invoke this method to perform the extraction. Returns true if
            any text is actually extracted, false otherwise.
        """
        for line in self.input_stream:
            # Check terminate, regardless of state:
            if self.check_pattern(self.terminate, line, self.active_mode):
                return self.wrote_something
            # Change state if flagged to do so:
            if self.active_mode is None:
                for mode in self.modes:
                    if self.check_pattern(mode['start'], line):
                        self.active_mode = mode
                        break
                continue
            # We are extracting in some mode. See if we should stop:
            if self.check_pattern(self.active_mode['stop'], line):
                self.active_mode = None
                continue
            # Extract all other lines in the normal way:
            self.extract_line(line)
        return self.wrote_something

    def replace_line(self, line):
        """Apply the specified replacements to the line and return it"""
        for item in self.active_mode['replace']:
            pattern = item[0] if isinstance(item, tuple) else item
            match_object = pattern.search(line)
            if match_object:
                if isinstance(item, tuple):
                    return match_object.expand(item[1])
                if match_object.lastindex:
                    return match_object[match_object.lastindex]
                return ''
        return line

    def extract_line(self, line):
        """Copy line to the output stream, applying all of the
           specified replacements.
        """
        line = self.replace_line(line)
        self.transcribe(line)


def get_config_site_dir(config_file_path):
    orig_config = mkdocs_config.load_config(config_file_path)
    utils.log.debug(
        "mkdocs-simple-plugin: loading file: {}".format(config_file_path))

    utils.log.debug(
        "mkdocs-simple-plugin: User config site_dir: {}".format(
            orig_config.data['site_dir']))
    return orig_config.data['site_dir']


class SimplePlugin(BasePlugin):
    """
    SimplePlugin adds documentation throughout your repo to a mkdocs wiki.
    """

    # md
    # ### Configuration scheme
    # /md
    config_scheme = (
        # md
        # #### include_folders
        # Directories whose name matches a glob pattern in this list will be
        # searched for documentation
        # /md
        ('include_folders', config_options.Type(list, default=['*'])),

        # md
        # #### ignore_folders
        # Directories whose name matches a glob pattern in this list will NOT be
        # searched for documentation.
        # /md
        ('ignore_folders', config_options.Type(list, default=[])),

        # md
        # #### ignore_hidden
        # Hidden directories will not be searched if this is true.
        # /md
        ('ignore_hidden', config_options.Type(bool, default=True)),

        # md
        # #### merge_docs_dir
        # If true, the contents of the docs directory (if any) will be merged
        # at the same level as all other documentation.
        # Otherwise, the docs directory will be retained as a subdirectory in
        # the result.
        # /md
        ('merge_docs_dir', config_options.Type(bool, default=True)),

        # md
        # #### include_extensions
        # Any file in the searched directories whose name contains a string in
        # this list will simply be copied to the generated documentation.
        # /md
        ('include_extensions',
            config_options.Type(
                list,
                default=[
                    ".bmp", ".tif", ".tiff", ".gif", ".svg", ".jpeg",
                    ".jpg", ".jif", ".jfif", ".jp2", ".jpx", ".j2k",
                    ".j2c", ".fpx", ".pcd", ".png", ".pdf", "CNAME"
                ])),
        # md
        # #### semiliterate
        # The semiliterate settings allows the extraction of markdown from
        # inside source files.
        # It is defined as a list of blocks of settings for different
        # filename patterns (typically matching filename extensions).
        # All regular expression parameters use ordinary Python `re` syntax.
        # The settings in each block are:
        #
        # ##### pattern
        # Any file in the searched directories whose name contains this
        # required regular expression parameter will be scanned.
        #
        # ##### destination
        # By default, the extracted documentation will be copied to a file
        # whose name is generated by removing the (last) extension from the
        # original filename, if any, and appending `.md`. However, if this
        # parameter is specified, it will be expanded as a template using
        # the match object from matching "pattern" against the filename,
        # to produce the name of the destination file.
        #
        # ##### terminate
        # If specified, all extraction from the file is terminated when
        # a line containing this regexp is encountered (whether or not
        # any extraction is currently active per the parameters below).
        # The last matching group in the `terminate` expression, if any,
        # is written to the destination file; note that "start" and "stop"
        # below share that same behavior.
        #
        # ##### extract
        # This parameter determines what will be extracted from a scanned
        # file that matches the pattern above. Its value should be a block
        # or list of blocks of settings. Each block determines one mode of
        # extraction from the scanned file, and can specify:
        #
        # ###### start
        # If no mode of extraction is active, and a line in the scanned
        # file matches this regexp, then this mode of extraction begins
        # with the next line. Only the first mode whose `start` expression
        # matches is activated, so at most one mode of extraction can be active
        # at any time. When an extraction is active, lines from the scanned
        # file are copied to the destination file (possibly modified by
        # the "replace" parameter below).
        #
        # ###### stop
        # When this extraction mode is active and a line containing this
        # (optional) regexp is encountered, this mode becomes inactive.
        # The `simple` plugin will begin searching for further occurrences
        # of `start` expressions on the _next_ line of the scanned file.
        #
        # ###### replace
        #
        # The `replace` parameter allows extracted lines from a file to
        # be transformed in simple ways by regular expressions, for
        # example to strip leading comment symbols if necessary.
        #
        # The `replace` parameter is a list of substitutions to attempt. Each
        # substitution is specified either by a two-element list of a
        # regular expression and a template, or by just a regular expression. In
        # each extracted line, the regular expression from each
        # substitution in turn is searched for.
        # If none match, the line is transcribed unchanged.
        # For the first one that matches, the template (expanded with the
        # results of the match) is transcribed in place of the line.
        # If there is no template, then just the last matching group is
        # transcribed, or nothing at all is transcribed if there is no last
        # matching group.
        # This latter convention makes it easy to selectively drop
        # lines that contain a given regular expression.
        #
        # Once one of the
        # `replace` patterns matches, processing stops; no further expressions
        # are checked.
        #
        # Note that the (last) extraction mode (if any) with no `start`
        # parameter is active beginning with the first line of the scanned file;
        # there is no way such a mode can be reactivated if it stops.
        # This convention allows for convenient "front-matter" extraction.
        #
        # ##### Standard behavior
        #
        # The default semiliterate patterns invoke the following automatic
        # extraction of markdown content from your source files: (Note that if you
        # add your own semiliterate patterns but want to also use any of these,
        # you must reiterate the default pattern or patterns you want in your
        # `mkdocs.yml` file.)
        #
        # /md
        ('semiliterate',
            config_options.Type(
                list,
                default=[
                    {
                        # md
                        # * From Python (`.py`) files: triple-quoted strings
                        #   starting with `""" md` and ending with `"""`, as
                        #   well as line-comment blocks
                        #   starting with `# md` and ending with `# /md`, from
                        #   which leading `# ` is stripped.
                        # /md
                        'pattern': r'\.py$',
                        'extract': [
                            {'start': r'"""\smd$', 'stop': r'"""'},
                            {
                                'start': r'#\smd$',
                                'stop': r'#\s\/md$',
                                'replace': [r'^\s*# ?(.*\n?)$']
                            }
                        ]
                    },
                    {
                        # md
                        #
                        # * From C, C++, and Javascript files: block comments
                        #   starting with `/** md` and ending with `**/`.
                        # /md
                        'pattern': r'\.(cpp|cc?|h|hpp|js)$',
                        'extract': {
                            'start': r'/\*\* md',
                            'stop': r'\*\*/'
                        }
                    },
                    {
                        # md
                        #
                        # * And from YAML and Dockerfiles: line-comment blocks
                        #   starting with `# md` and ending with `# /md`.
                        # /md
                        'pattern': r'Dockerfile$|\.(dockerfile|ya?ml)$',
                        'extract': {
                            'start': r'#\smd$',
                            'stop': r'#\s\/md$',
                            # Remove the leading `#` from all extracted lines:
                            'replace': [r'^\s*#? ?(.*\n?)$']
                        }
                    },
                ]))
    )

    def on_config(self, config, **kwargs):
        # Dump configuration to documentation
        config['mkdocs_simple_config'] = yaml.dump(
            self.config.data,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            encoding=None)
        # Create a temporary build directory, and set some options to serve it
        # PY2 returns a byte string by default. The Unicode prefix ensures a
        # Unicode string is returned. And it makes MkDocs temp dirs easier to
        # identify.
        self.build_docs_dir = tempfile.mkdtemp(
            prefix="mkdocs_simple_{}".format(
                os.path.basename(os.path.dirname(config.config_file_path))))
        utils.log.debug("mkdocs-simple-plugin: build_docs_dir: {}".format(
            self.build_docs_dir))
        # Clean out build folder on config
        shutil.rmtree(self.build_docs_dir, ignore_errors=True)
        os.makedirs(self.build_docs_dir, exist_ok=True)
        # Save original docs directory location
        self.orig_docs_dir = config['docs_dir']
        # Update the docs_dir with our temporary one
        config['docs_dir'] = self.build_docs_dir
        return config

    def on_pre_build(self, config, **kwargs):
        self.include_folders = self.config['include_folders']
        self.ignore_folders = self.config['ignore_folders']
        self.ignore_hidden = self.config['ignore_hidden']
        self.include_extensions = utils.markdown_extensions + \
            self.config['include_extensions']
        self.merge_docs_dir = self.config['merge_docs_dir']
        self.semiliterate = []
        for item in self.config['semiliterate']:
            self.semiliterate.append(
                # Note it is critical that the original item not be modified,
                # so if this code is changed, the entry added to semiliterate
                # needs to remain at least a shallow copy of `item`.
                dict(item, pattern=re.compile(item['pattern'])))

        # Always ignore the output paths
        self.ignore_paths = [get_config_site_dir(config.config_file_path),
                             config['site_dir'],
                             self.build_docs_dir]
        # Copy contents of docs directory if merging
        if self.merge_docs_dir and os.path.exists(self.orig_docs_dir):
            self.copy_docs_directory(self.orig_docs_dir, self.build_docs_dir)
            self.ignore_paths += [self.orig_docs_dir]
        # Copy all of the valid doc files into build_docs_dir
        self.paths = self.build_docs()

    def on_serve(self, server, config, **kwargs):
        builder = list(server.watcher._tasks.values())[0]['func']

        # still watch the original docs/ directory
        if os.path.exists(self.orig_docs_dir):
            server.watch(self.orig_docs_dir, builder)

        # watch all the doc files
        for orig, _ in self.paths:
            server.watch(orig, builder)

        return server

    def in_search_directory(self, directory, root):
        if self.ignore_hidden and (directory[0] == "."
                                   or directory == "__pycache__"):
            return False
        if any(fnmatch.fnmatch(directory, filter)
                for filter in self.ignore_folders):
            return False
        if os.path.abspath(os.path.join(root, directory)) in self.ignore_paths:
            return False
        return True

    def in_include_directory(self, directory):
        return any(fnmatch.fnmatch(directory, filter)
                   for filter in self.include_folders)

    def in_extensions(self, file):
        return any(extension in file for extension in self.include_extensions)

    def build_docs(self):
        paths = []
        for root, directories, files in os.walk("."):
            if self.in_include_directory(root):
                document_root = self.build_docs_dir + root[1:]
                for f in files:
                    paths.extend(self.copy_file(root, f, document_root))
                    paths.extend(self.extract_from(root, f, document_root))
            directories[:] = [d for d in directories
                              if self.in_search_directory(d, root)]
        return paths

    def copy_file(self, from_directory, name, destination_directory):
        """Copy the file in _from_directory_ named _name_ to the
           destination_directory.
        """
        original = "{}/{}".format(from_directory, name)
        if self.in_extensions(name):
            new_file = "{}/{}".format(destination_directory, name)
            try:
                os.makedirs(destination_directory, exist_ok=True)
                shutil.copy(original, new_file)
                utils.log.debug("mkdocs-simple-plugin: {} --> {}".format(
                    original, new_file))
                return [(original, new_file)]
            except Exception as e:
                utils.log.warn(
                    "mkdocs-simple-plugin: error! {}.. skipping {}".format(
                        e, original))
        return []

    def extract_from(self, from_directory, name, destination_directory):
        """Extract content from the file in _from_directory_ named _name_
           to a file or files in _destination_directory_, as specified by
           the semiliterate parameters.
        """
        new_paths = []
        original = "{}/{}".format(from_directory, name)
        for item in self.semiliterate:
            name_match = item['pattern'].search(name)
            if name_match:
                new_name = os.path.splitext(name)[0] + '.md'
                if 'destination' in item:
                    new_name = name_match.expand(item['destination'])
                new_file = LazyFile(destination_directory, new_name)
                with open(original) as original_file:
                    utils.log.debug(
                        "mkdocs-simple-plugin: Scanning {}...".format(original))
                    productive = self.try_extraction(
                        original_file, from_directory, new_file, **item)
                    new_file.close()
                    if productive:
                        new_path = "{}/{}".format(destination_directory,
                                                  new_name)
                        utils.log.debug(
                            "        ... extracted {}".format(new_path))
                        new_paths.append((original, new_path))
        return new_paths

    def try_extraction(self, original_file, root, new_file, **kwargs):
        """Attempt to extract documentation from a single file
           according to specific extraction parameters
        """
        extraction = StreamExtract(
            original_file, new_file, include_root=root, **kwargs)
        return extraction.extract()

    def copy_docs_directory(self, root_source_directory,
                            root_destination_directory):
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
