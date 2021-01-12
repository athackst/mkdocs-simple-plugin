""" md
MkDocs Simple Plugin
====================

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
                 start=None, terminate=None, stop=None, replace=[],
                 include_root=None,
                 **ignore_other_kwargs):
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.start = re.compile(start)
        self.terminate = (terminate is not None) and re.compile(terminate)
        self.stop = (stop is not None) and re.compile(stop)
        self.replace = []
        for item in replace:
            if isinstance(item, str):
                self.replace.append(re.compile(item))
            else:
                self.replace.append((re.compile(item[0]), item[1]))
        self.include_root = include_root
        self.wrote_something = False
        self.extracting = False

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
            if self.check_pattern(self.terminate, line, self.extracting):
                return self.wrote_something
            # Change state if flagged to do so:
            if not self.extracting:
                if self.check_pattern(self.start, line):
                    self.extracting = True
                continue
            # We are extracting. See if we should stop:
            if self.check_pattern(self.stop, line):
                self.extracting = False
                continue
            # Extract all other lines in the normal way:
            self.extract_line(line)
        return self.wrote_something

    def replace_line(self, line):
        """Apply the specified replacements to the line and return it"""
        for item in self.replace:
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
        # at the same level as all other documentation,
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
        # It is defined as a list of extraction settings.  These settings are:
        #
        # ##### pattern
        # Any file in the searched directories whose name contains this
        # required regular expression parameter will be scanned.
        #
        # ##### destination
        # By default, the extracted documentation will be copied to a file
        # whose name is generated by replacing the last matching group
        # in the "pattern" parameter with `.md`. However, if the following
        # parameter is specified, it will be expanded as a template using
        # the match object from matching "pattern" against the filename,
        # to produce the name of the extracted file.
        #
        # ##### start
        # Lines from the scanned file will be ignored until a line
        # containing this required regular expression parameter is
        # encountered. As with the other parameters ("stop" and "terminate")
        # controlling extraction, the last matching group in the "start"
        # expression, if any, will be written to the extracted file.
        # Subsequent lines, possibly with the transformations specified
        # by the "replace" parameter below, will be written to the
        # extracted file.
        #
        # ##### stop
        # Whenever a line containing this optional regexp is encountered,
        # extraction of the file will be suspended until the next occurrence
        # of "start" (if any) is encountered.
        #
        # ##### terminate
        # If specified, all extraction from the file is terminated when
        # a line containing this regexp is encountered. Note that if
        # "terminate" occurs before "start" nothing will be extracted
        # from the file.
        #
        # ##### replace
        #
        # The `replace` parameter allows extracted lines from a file to
        # be transformed in simple ways by regular expressions.
        # One possible use of `replace` is to strip leading line-comment
        # symbols from documentation embedded in such places as YAML files that
        # only have line comments, rather than block comments.
        #
        # The `replace` parameter is a list of substitutions to attempt. Each
        # substitution is specified either by a two-element list of a (Python)
        # regular expression and a template, or by just a regular expression. In
        # each line that `simple` extracts, the regular expression from each
        # substitution in turn is searched for.
        # If none match, the line is transcribed unchanged.
        # For the first one that matches, the template is transcribed in place
        # of the line.
        # If there is no template, then just the last matching group is
        # transcribed, or nothing at all is transcribed if there is no last
        # matching group.
        # This latter convention makes it easy to selectively drop
        # lines that contain a given regular expression.
        #
        # Note that once one of the
        # `replace` patterns matches, processing stops; no further expressions
        # are checked.
        # /md
        ('semiliterate',
            config_options.Type(
                list,
                default=[
                    {
                        'pattern': r'(\.py)$',
                        'start': r'"""\smd$|#\smd$',
                        'stop': r'"""|#\s\/md$',
                        # Remove the leading `#` from all extracted lines:
                        'replace': [(r'^\s*#\s(.*)$', r'\1\n')]
                    },
                    {
                        'pattern': r'(\.cpp)$|(\.c)$|(\.cc)$|(\.h)$|(\.hpp)|(\.js)$',
                        'start': r'/\*\* md',
                        'stop': r'\*\*/'
                    },
                    {
                        'pattern': r'Dockerfile()$|(\.dockerfile)$|(\.yml)$|(\.yaml)$',
                        'start': r'#\smd$',
                        'stop': r'#\s\/md$',
                        # Remove the leading `#` from all extracted lines:
                        'replace': [(r'^\s*#?\s(.*)$', r'\1\n')]
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
            item['pattern'] = re.compile(item['pattern'])
            self.semiliterate.append(item)

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
                if 'destination' in item:
                    new_name = name_match.expand(item['destination'])
                else:
                    if not name_match.lastindex:
                        raise LookupError(
                            "mkdocs-simple-plugin: No last group in match of" +
                            "{} to {} and no destination".format(
                                item['pattern'], name))
                    new_name = (name[:name_match.start(name_match.lastindex)] +
                                '.md' +
                                name[name_match.end(name_match.lastindex):])
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
