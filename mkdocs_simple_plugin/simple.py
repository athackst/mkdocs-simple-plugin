"""Simple module handles document extraction from source files."""
import fnmatch
import os
import pathlib
import stat

from shutil import copy2 as copy
from dataclasses import dataclass

from mkdocs import utils
from mkdocs_simple_plugin.semiliterate import Semiliterate


@dataclass
class SimplePath:
    """Paths processed by Simple."""
    output_root: str
    output_relpath: str
    input_path: str


class Simple():
    """Mkdocs Simple Plugin"""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            build_dir: str,
            folders: list,
            include: list,
            ignore: list,
            ignore_hidden: bool,
            ignore_paths: list,
            semiliterate: list,
            **kwargs):
        """Initialize module instance with settings.

        Args:
            build_dir (str): Output directory for processed files
            folders (list): Glob of folders to search for files
            include (list): Glob of filenames to copy directly to output
            ignore (list): Glob of paths to exclude
            ignore_hidden (bool): Whether to ignore hidden files for processing
            ignore_paths (list): Absolute filepaths to exclude
            semiliterate (list): Settings for processing file content in
                Semiliterate

        """
        self.build_dir = build_dir
        self.folders = set(folders)
        self.doc_glob = set(include)
        self.ignore_glob = set(ignore)
        self.ignore_hidden = ignore_hidden  # to be deprecated
        self.hidden_prefix = set([".", "__"])  # to be deprecated
        self.ignore_paths = set(ignore_paths)
        self.semiliterate = []
        for item in semiliterate:
            self.semiliterate.append(Semiliterate(**item))

    def get_files(self) -> list:
        """Get a list of files to process, excluding ignored files."""
        files = []
        # Get all of the entries that match the include pattern.
        entries = []
        for pattern in self.folders:
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
            if os.path.abspath(path).startswith(ignored):
                return True

        # Update ignore patterns from .mkdocsignore file
        mkdocsignore = os.path.join(base_path, ".mkdocsignore")
        if os.path.exists(mkdocsignore):
            ignore_list = []
            with open(mkdocsignore, mode="r", encoding="utf-8") as txt_file:
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

    def is_doc_file(self, name: str) -> bool:
        """Check if file is a desired doc file."""
        def match_pattern(name, pattern):
            return fnmatch.fnmatch(name, pattern) or pattern in name

        return any(match_pattern(name, pattern) for pattern in self.doc_glob)

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
        # Check if file is text based
        try:
            with open(name, 'r', encoding='utf-8') as f:
                _ = f.read()
        except UnicodeDecodeError:
            return False

        # Check if file is hidden and should ignore
        if self.ignore_hidden:
            is_hidden = has_hidden_prefix(name) or has_hidden_attribute(name)
            return not is_hidden
        return True

    def merge_docs(self, from_dir, dirty=False):
        """Merge docs directory"""
        if not os.path.exists(from_dir):
            return
        # Copy contents of docs directory if merging
        for source_directory, _, files in os.walk(from_dir):
            destination_directory = source_directory.replace(
                from_dir, self.build_dir, 1)
            os.makedirs(destination_directory, exist_ok=True)
            for file_ in files:
                source_file = os.path.join(source_directory, file_)
                destination_file = os.path.join(destination_directory, file_)
                if os.path.exists(destination_file):
                    if dirty and os.stat(source_file).st_mtime <= os.stat(
                            destination_file).st_mtime:
                        continue
                    os.remove(destination_file)
                copy(source_file, destination_directory)
                utils.log.info(
                    "mkdocs-simple-plugin: %s/* --> %s/*",
                    source_file, destination_file)
        self.ignore_paths.add(from_dir)

    def build_docs(
            self,
            dirty=False,
            last_build_time=None,
            do_copy=False) -> list:
        """Build the docs directory from workspace files."""
        paths = []
        files = self.get_files()
        for file in files:
            if not os.path.isfile(file):
                continue
            if dirty and last_build_time and (
                    os.path.getmtime(file) <= last_build_time):
                continue
            from_dir = os.path.dirname(file)
            name = os.path.basename(file)
            build_prefix = os.path.normpath(
                os.path.join(self.build_dir, from_dir))

            doc_paths = self.get_doc_file(
                from_dir, name, build_prefix, do_copy)
            if doc_paths:
                paths.append(
                    SimplePath(
                        output_root=".",
                        output_relpath=os.path.relpath(path=file, start="."),
                        input_path=file)
                )
                utils.log.info("mkdocs-simple-plugin: Added %s", file)
                continue

            extracted_paths = self.try_extract(from_dir, name, build_prefix)
            for path in extracted_paths:
                paths.append(
                    SimplePath(
                        output_root=self.build_dir,
                        output_relpath=os.path.relpath(
                            path=path,
                            start=self.build_dir),
                        input_path=file))
                utils.log.info(
                    "mkdocs-simple-plugin: Added %s->%s", file, path)
            if extracted_paths:
                continue

        return paths

    def try_extract(self, from_dir: str, name: str, to_dir: str) -> list:
        """Extract content from file into destination.

        Returns the name of the file extracted if extractable.
        """
        # Check if it's hidden
        path = os.path.join(from_dir, name)
        if not self.should_extract_file(path):
            return []
        for item in self.semiliterate:
            paths = item.try_extraction(from_dir, name, to_dir)
            if paths:
                return paths

        return []

    def get_doc_file(
            self,
            from_dir: str,
            name: str,
            to_dir: str,
            do_copy: bool) -> list:
        """Copy file with the same name to a new directory.

        Returns true if file copied.
        """
        original = os.path.join(from_dir, name)

        if not self.is_doc_file(os.path.join(from_dir, name)):
            return []

        if do_copy:
            destination = os.path.join(to_dir, name)
            os.makedirs(to_dir, exist_ok=True)
            copy(original, destination)
        return [original]
