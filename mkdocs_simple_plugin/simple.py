"""Simple module handles document extraction from source files."""
import fnmatch
import os
import pathlib
import stat
from typing import List, Dict

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
        self.ignore_hidden = ignore_hidden  # TODO[athackst] deprecate
        self.hidden_prefix = set([".", "__"])  # TODO[athackst] deprecate
        self.ignore_paths = set(ignore_paths)
        self.semiliterate = []
        for item in semiliterate:
            self.semiliterate.append(Semiliterate(**item))
        self.ignore_patterns: Dict[pathlib.Path, List[str]] = {}
        self.root_path: pathlib.Path = pathlib.Path()

    def process_mkdocsignore_files(self):
        """Process all .mkdocsignore files and update ignore_glob."""
        for mkdocsignore in self.root_path.rglob('.mkdocsignore'):
            relative_path = mkdocsignore.parent.relative_to(self.root_path)
            patterns = []
            with mkdocsignore.open(mode="r", encoding="utf-8") as txt_file:
                for line in txt_file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)

            if not patterns:
                # If .mkdocsignore is empty, ignore everything in this directory
                # and below
                pattern = str(relative_path / '**')
                self.ignore_glob.add(pattern)
            else:
                for pattern in patterns:
                    if relative_path != pathlib.Path('.'):
                        pattern = str(relative_path / pattern)
                    self.ignore_glob.add(pattern)

    def process_ignore_folders(self):
        """Update ignore glob to include folders."""
        self.ignore_glob.update(
            [f"{pattern}/**" for pattern in self.ignore_glob])

    def get_files(self) -> List[str]:
        """Get a list of files to process, excluding ignored files."""
        # Process all .mkdocsignore files first
        self.process_mkdocsignore_files()
        self.process_ignore_folders()  # TODO[athackst] deprecate
        files = set()
        for pattern in self.folders:
            for entry in pathlib.Path().glob(pattern):
                if entry.is_dir():
                    files.update(str(f) for f in entry.rglob(
                        '*') if self.is_valid_file(f))
                elif self.is_valid_file(entry):
                    files.add(str(entry))
        return list(files)

    def is_valid_file(self, path: pathlib.Path) -> bool:
        """Check if file is valid (not ignored and matches doc_glob)."""
        if self.is_ignored(path):
            return False
        if not path.is_file():
            return False
        return True

    def is_ignored(self, path: pathlib.Path) -> bool:
        """Check if path should be ignored."""
        rel_path = path.relative_to(self.root_path)

        # Check ignore_paths (absolute paths)
        if any(path.resolve().is_relative_to(ignored)
               for ignored in self.ignore_paths):
            return True

        # Check all ignore patterns
        return any(fnmatch.fnmatch(str(rel_path), pattern)
                   for pattern in self.ignore_glob)

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
