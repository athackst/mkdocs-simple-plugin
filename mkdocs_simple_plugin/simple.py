"""Simple module handles document extraction from source files."""
import os
import fnmatch
import shutil
import stat
import sys
import glob

from mkdocs import utils
from mkdocs_simple_plugin.semiliterate import Semiliterate


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
