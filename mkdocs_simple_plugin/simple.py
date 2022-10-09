"""Simple module handles document extraction from source files."""
import os
import fnmatch
import shutil
import stat
import sys
import pathlib

from mkdocs import utils
from mkdocs_simple_plugin.semiliterate import Semiliterate


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
        """Initialize module instance with settings.

        Args:
            build_docs_dir (str): Output directory for processed files
            include_folders (list): Glob of folders to search for files
            include_extensions (list): Glob of filenames to copy directly to
                output
            ignore_folders (list): Glob of paths to exclude
            ignore_hidden (bool): Whether to ignore hidden files for processing
            ignore_paths (list): Absolute filepaths to exclude
            semiliterate (dict): Settings for processing file content in
                Semiliterate

        """
        self.build_dir = build_docs_dir
        self.include_folders = set(include_folders)
        self.copy_glob = set(include_extensions)
        self.ignore_glob = set(ignore_folders)
        self.ignore_hidden = ignore_hidden
        self.hidden_prefix = set([".", "__"])
        self.ignore_paths = set(ignore_paths)
        self.semiliterate = []
        for item in semiliterate:
            self.semiliterate.append(Semiliterate(**item))

    def get_files(self) -> list:
        """Get a list of files to process, excluding ignored files."""
        files = []
        # Get all of the entries that match the include pattern.
        entries = []
        for pattern in self.include_folders:
            entries.extend(pathlib.Path().glob(pattern))
        # Ignore any entries that match the ignore pattern
        entries[:] = [
            entry for entry in entries
            if not self.is_path_ignored(str(entry))]
        # Add any files
        files[:] = [
            os.path.normpath(entry) for entry in entries if entry.is_file()]
        # Iterate through directories to get files
        for entry in entries:
            for root, directories, filenames in os.walk(entry):
                files.extend([os.path.join(root, f)
                             for f in filenames if not self.is_ignored(root, f)]
                             )
                directories[:] = [
                    d for d in directories if not self.is_ignored(root, d)]
        return files

    def is_ignored(self, base_path: str, name: str) -> bool:
        """Check if directory and filename should be ignored."""
        return self.is_path_ignored(os.path.join(base_path, name))

    def is_path_ignored(self, path: str = None) -> bool:
        """Check if path should be ignored."""
        path = os.path.normpath(path)
        base_path = os.path.dirname(path)

        # Check if its an internally required ignore path
        for ignored in self.ignore_paths:
            if ignored in os.path.abspath(path):
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
            self.ignore_glob.update(
                set(os.path.join(base_path, filter) for filter in ignore_list))
        # Check for ignore paths in patterns
        if any(fnmatch.fnmatch(path, filter)
                for filter in self.ignore_glob):
            return True
        return False

    def should_copy_file(self, name: str) -> bool:
        """Check if file should be copied."""
        def match_pattern(name, pattern):
            return fnmatch.fnmatch(name, pattern) or pattern in name

        return any(match_pattern(name, pattern) for pattern in self.copy_glob)

    def should_extract_file(self, name: str):
        """Check if file should be extracted."""
        def has_hidden_attribute(filepath):
            """Returns true if hidden attribute is set."""
            try:
                return bool(os.stat(filepath).st_file_attributes &
                            stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, AssertionError):
                return False

        def has_hidden_prefix(filepath):
            """Returns true if the file starts with a hidden prefix."""
            parts = filepath.split(os.path.sep)

            def hidden_prefix(name):
                if name == ".":
                    return False
                return any(name.startswith(pattern)
                           for pattern in self.hidden_prefix)
            return any(hidden_prefix(part) for part in parts)

        extract = True
        if self.ignore_hidden:
            is_hidden = has_hidden_prefix(name) or has_hidden_attribute(name)
            extract = not is_hidden

        return extract

    def merge_docs(self, from_dir):
        """Merge docs directory"""
        # Copy contents of docs directory if merging
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

        if os.path.exists(from_dir):
            copy_directory(from_dir, self.build_dir)
            self.ignore_paths.add(from_dir)

    def build_docs(self) -> list:
        """Build the docs directory from workspace files."""
        paths = []
        files = self.get_files()
        for file in files:
            if not os.path.isfile(file):
                continue
            from_dir = os.path.dirname(file)
            name = os.path.basename(file)
            build_prefix = os.path.normpath(
                os.path.join(self.build_dir, from_dir))

            if (self.try_copy_file(from_dir, name, build_prefix) or
                    self.try_extract(from_dir, name, build_prefix)):
                paths.append(file)
        return paths

    def try_extract(self, from_dir: str, name: str, to_dir: str) -> bool:
        """Extract content from file into destination.

        Returns the name of the file extracted if extractable.
        """
        # Check if it's hidden
        path = os.path.join(from_dir, name)
        if not self.should_extract_file(path):
            return False
        for item in self.semiliterate:
            if item.try_extraction(from_dir, name, to_dir):
                return True

        return False

    def try_copy_file(self, from_dir: str, name: str, to_dir: str) -> bool:
        """Copy file with the same name to a new directory.

        Returns true if file copied.
        """
        original = os.path.join(from_dir, name)
        new_file = os.path.join(to_dir, name)

        if not self.should_copy_file(name):
            return False
        try:
            os.makedirs(to_dir, exist_ok=True)
            shutil.copy(original, new_file)
            utils.log.info("mkdocs-simple-plugin: %s --> %s",
                           original, new_file)
            return True
        except (OSError, IOError, UnicodeDecodeError) as error:
            utils.log.warning(
                "mkdocs-simple-plugin: %s.. skipping %s",
                error, original)
        return False
