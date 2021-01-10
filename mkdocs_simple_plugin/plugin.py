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
                f"{self.file_directory}/{self.file_name}", 'w')
        self.file_object.write(arg)

    def close(self):
        if self.file_object is not None:
            self.file_object.close()


class StreamExtract:
    """
    Instantiating a StreamExtract object copies _input_stream_ to
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
        self.extract()

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
        """ Actually performs the extraction """
        for line in self.input_stream:
            # Check terminate, regardless of state:
            if self.check_pattern(self.terminate, line, self.extracting):
                return
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

    def productive(self):
        """Returns true if any text was actually extracted"""
        return self.wrote_something


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

    Usage:

        site_name: your_site_name
        plugins:
        - simple:
            # Optional setting to only include specific folders
            include_folders: ["*"]
            # Optional setting to ignore specific folders
            ignore_folders: []
            # Optional setting to specify if hidden folders should be ignored
            ignore_hidden: True
            # Optional setting to specify other extensions besides md files to be copied
            include_extensions: eval(common_extensions())
            # Optional setting to merge the docs directory with other documentation
            merge_docs_dir: True
    """
    config_scheme = (
        ('include_folders', config_options.Type(list, default=['*'])),
        ('ignore_folders', config_options.Type(list, default=[])),
        ('ignore_hidden', config_options.Type(bool, default=True)),
        ('merge_docs_dir', config_options.Type(bool, default=True)),
        ('include_extensions',
            config_options.Type(
                list,
                default=[
                    ".bmp", ".tif", ".tiff", ".gif", ".svg", ".jpeg",
                    ".jpg", ".jif", ".jfif", ".jp2", ".jpx", ".j2k",
                    ".j2c", ".fpx", ".pcd", ".png", ".pdf", "CNAME"
                ])),
        ('semiliterate',
            config_options.Type(
                list,
                default=[
                    {
                        'pattern': r'(\.py)$',
                        'start': r'"""\smd',
                        'stop': r'"""'
                    },
                    {
                        'pattern': r'(\.py)$',
                        'start': r'"""\smd',
                        'stop': r'"""'
                    },
                    {
                        'pattern': r'(\.[^.]*)$',
                        'start': r'/\*\* md',
                        'stop': r'\*\*/'
                    }]))
    )

    def on_config(self, config, **kwargs):
        # Create a temporary build directory, and set some options to serve it
        # PY2 returns a byte string by default. The Unicode prefix ensures a Unicode
        # string is returned. And it makes MkDocs temp dirs easier to identify.
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

        # # Always ignore the output paths
        self.ignore_paths = [
            get_config_site_dir(config.config_file_path), config['site_dir'],
            self.build_docs_dir
        ]
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
                    if self.in_extensions(f):
                        paths.extend(self.copy_file(root, f, document_root))
                    else:
                        paths.extend(self.extract_from(root, f, document_root))
            directories[:] = [
                d for d in directories if self.in_search_directory(d, root)
            ]
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
                new_name = (name[:name_match.start(name_match.lastindex)] +
                            '.md' +
                            name[name_match.end(name_match.lastindex):])
                if 'destination' in item:
                    new_name = name_match.expand(item['destination'])
                new_file = LazyFile(destination_directory, new_name)
                with open(original) as original_file:
                    extraction = StreamExtract(original_file,
                                               new_file,
                                               include_root=from_directory,
                                               **item)
                    new_file.close()
                    if extraction.productive():
                        new_path = "{}/{}".format(destination_directory,
                                                  new_name)
                        utils.log.debug(
                            "mkdocs-simple-plugin: {} --> {}".format(
                                original, new_path))
                        new_paths.append((original, new_path))
        return new_paths

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
