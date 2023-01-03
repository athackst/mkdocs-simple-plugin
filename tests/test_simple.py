#!/usr/bin/env python
"""Test mkdocs_simple_plugin.simple"""
import unittest
from unittest.mock import patch
import stat
import os
from pyfakefs.fake_filesystem_unittest import TestCase

from mkdocs_simple_plugin import simple


class TestSimple(TestCase):
    """Test Simple class."""

    def setUp(self) -> None:
        """Set defaults"""
        self.default_settings = {
            "build_docs_dir": "/build_dir/",
            "include_folders": ["*"],
            "ignore_folders": [],
            "ignore_hidden": True,
            "include_extensions": [".md"],
            "ignore_paths": [],
            "semiliterate": {}
        }
        self.setUpPyfakefs()

    @patch("os.stat")
    def test_should_extract_file(self, os_stat):
        """Test should_extract_file for correctness."""
        simple_test = simple.Simple(**self.default_settings)
        # Check ignore_hidden
        simple_test.ignore_hidden = True
        os_stat.return_value.st_file_attributes = 0
        self.assertTrue(simple_test.should_extract_file('test.md'))
        self.assertTrue(simple_test.should_extract_file('./folder/test.md'))
        self.assertFalse(simple_test.should_extract_file('__pycache__'))
        self.assertFalse(simple_test.should_extract_file('.mkdocsignore'))
        self.assertFalse(simple_test.should_extract_file(
            ".git/objects/34/49807110bdc8"))
        # Check hidden file attribute
        os_stat.return_value.st_file_attributes = stat.FILE_ATTRIBUTE_HIDDEN
        self.assertFalse(simple_test.should_extract_file('/test/file'))

    def test_ignored_default(self):
        """Test ignored files."""
        simple_test = simple.Simple(**self.default_settings)
        self.fs.create_file("directory/file")
        self.assertFalse(
            simple_test.is_ignored(
                base_path="directory",
                name="file"
            )
        )

    def test_ignored_paths(self):
        """Test ignored files."""
        simple_test = simple.Simple(**self.default_settings)
        base_path = "directory"
        name = "test.md"
        path = os.path.join(base_path, name)
        self.fs.create_file(path)

        self.assertFalse(
            simple_test.is_ignored(
                base_path=base_path,
                name=name))

        abs_path = os.path.abspath(os.path.join(base_path, name))
        simple_test.ignore_paths = [abs_path]
        self.assertTrue(simple_test.is_ignored(base_path=base_path, name=name))

    def test_ignored_config(self):
        """Test ignored files from config."""
        self.default_settings["ignore_folders"] = ["test/*"]
        simple_test = simple.Simple(**self.default_settings)
        self.fs.create_file("directory/test.md")
        self.assertFalse(
            simple_test.is_ignored(base_path="directory", name="test.md"))
        self.fs.create_file("test/file.md")
        self.assertTrue(
            simple_test.is_ignored(base_path="test", name="file.md"))

    def test_ignored_mkdocsignore(self):
        """Test mkdocsignore file."""
        simple_test = simple.Simple(**self.default_settings)

        self.fs.create_file("directory/.mkdocsignore", contents="*test*")
        self.fs.create_file("directory/test.md")
        self.assertTrue(
            simple_test.is_ignored(
                base_path="directory",
                name="test.md"))
        self.fs.create_file("./directory/hello.md")
        self.assertFalse(
            simple_test.is_ignored(
                base_path="directory",
                name="hello.md"))

        self.fs.create_file(".mkdocsignore", contents="*test*")
        self.fs.create_file("test.md")
        self.assertTrue(
            simple_test.is_ignored(
                base_path=".",
                name="test.md"))
        self.fs.create_file("hello.md")
        self.assertFalse(
            simple_test.is_ignored(
                base_path=".",
                name="hello.md"))
        self.assertIn("directory/*test*", simple_test.ignore_glob)
        self.assertIn("*test*", simple_test.ignore_glob)
        self.assertEqual(2, len(simple_test.ignore_glob))

    def test_ignored_mkdocsignore_empty(self):
        """Test empty mkdocsignore file."""
        simple_test = simple.Simple(**self.default_settings)
        self.fs.create_file("./directory/.mkdocsignore")
        self.fs.create_file("./directory/test.md")
        self.assertTrue(
            simple_test.is_ignored(
                base_path="./directory",
                name="test.md"))
        self.fs.create_file("hello.md")
        self.assertFalse(
            simple_test.is_ignored(
                base_path=".",
                name="hello.md"))
        self.assertIn("directory/*", simple_test.ignore_glob)
        self.assertEqual(1, len(simple_test.ignore_glob))

    def test_should_copy(self):
        """Test should_copy."""
        simple_test = simple.Simple(**self.default_settings)
        simple_test.copy_glob = ["*.md"]
        self.assertTrue(simple_test.should_copy_file(name="helloworld.md"))
        self.assertFalse(simple_test.should_copy_file(name="md.helloworld"))

        simple_test.copy_glob = [".pages"]
        self.assertTrue(simple_test.should_copy_file(name=".pages"))

    def test_get_files(self):
        """Test getting all files."""
        simple_test = simple.Simple(**self.default_settings)
        # /foo
        #  ├── baz.md
        #  ├── .pages
        #  └── bar
        #      ├── spam.md
        #      ├── hello.txt
        #      └── eggs.md
        #  └── bat
        #      ├── hello.md
        #      └── world.md
        # /goo
        #  └── day.md
        # boo.md
        self.fs.create_file("/foo/baz.md")
        self.fs.create_file("/foo/.pages")
        self.fs.create_file("/foo/bar/spam.md")
        self.fs.create_file("/foo/bar/hello.txt")
        self.fs.create_file("/foo/bar/eggs.md")
        self.fs.create_file("/foo/bat/hello.md")
        self.fs.create_file("/foo/bat/world.md")
        self.fs.create_file("/goo/day.md")
        self.fs.create_file("boo.md")

        files = simple_test.get_files()
        self.assertIn("foo/baz.md", files)
        self.assertIn("foo/.pages", files)
        self.assertIn("foo/bar/hello.txt", files)
        self.assertIn("foo/bar/eggs.md", files)
        self.assertIn("foo/bar/spam.md", files)
        self.assertIn("foo/bat/hello.md", files)
        self.assertIn("foo/bat/world.md", files)
        self.assertIn("goo/day.md", files)
        self.assertIn("boo.md", files)
        self.assertEqual(9, len(files))

    def test_get_files_ignore_folders(self):
        """Test getting all files not ignored."""
        simple_test = simple.Simple(**self.default_settings)
        # /foo
        #  ├── baz.md
        #  └── bar // ignore content in this folder
        #      ├── hello.txt
        #      ├── spam.md
        #      ├── eggs.md
        #      └── bat
        #          ├── hello.md
        #          └── world.md
        # /goo
        #  └── day.md
        #  └── night.md  // ignored from .mkdocsignore
        # boo.md
        # moo.md
        # .mkdocsignore
        self.fs.create_file("/foo/baz.md")
        self.fs.create_file("/foo/bar/hello.txt")
        self.fs.create_file("/foo/bar/spam.md")
        self.fs.create_file("/foo/bar/eggs.md")
        self.fs.create_file("/foo/bar/bat/hello.md")
        self.fs.create_file("/foo/bar/bat/world.md")
        self.fs.create_file("/goo/day.md")
        self.fs.create_file("/goo/night.md")
        self.fs.create_file("boo.md")
        self.fs.create_file(".mkdocsignore",
                            contents="\n".join([
                                "goo/night.md",
                                "moo.md"]))

        simple_test.ignore_glob = set(["foo/bar"])
        files = simple_test.get_files()
        self.assertIn("foo/baz.md", files)
        self.assertNotIn("foo/bar/hello.txt", files)
        self.assertNotIn("foo/bar/spam.md", files)
        self.assertNotIn("foo/bar/eggs.md", files)
        self.assertNotIn("foo/bar/bat/hello.md", files)
        self.assertNotIn("foo/bar/bat/world.md", files)
        self.assertIn("goo/day.md", files)
        self.assertNotIn("goo/night.md", files)
        self.assertIn("boo.md", files)
        self.assertIn(".mkdocsignore", files)
        self.assertEqual(4, len(files))

    def test_build_docs(self):
        """Test build docs."""
        simple_test = simple.Simple(**self.default_settings)

        # /foo
        #  ├── baz.md
        #  ├── .mkdocsignore //hidden + ignore settings
        #  ├── .pages //include in copy
        #  └── bar
        #      ├── hello.txt  // wrong extension
        #      ├── spam.md // ignored  from .mkdocsignore
        #      └── eggs.md
        #  └── bat // ignore directory
        #      ├── hello.md
        #      └── world.md
        # /goo // not included
        #  └── day.md
        # boo.md // not included
        self.fs.create_file("/foo/baz.md")
        self.fs.create_file("/foo/.mkdocsignore", contents="bar/spam.md*")
        self.fs.create_file("/foo/.pages")
        self.fs.create_file("/foo/bar/hello.txt")
        self.fs.create_file("/foo/bar/spam.md")
        self.fs.create_file("/foo/bar/eggs.md")
        self.fs.create_file("/foo/bat/hello.md")
        self.fs.create_file("/foo/bat/world.md")
        self.fs.create_file("/goo/day.md")
        self.fs.create_file("boo.md")

        simple_test.ignore_glob = set(["foo/bat/**"])
        simple_test.include_folders = set(["foo/"])
        simple_test.copy_glob = set(["*.md", ".pages"])

        paths = simple_test.build_docs()
        self.assertIn("foo/baz.md", paths)
        self.assertIn("foo/bar/eggs.md", paths)
        self.assertIn("foo/.pages", paths)
        self.assertEqual(3, len(paths))

    def test_build_docs_dirty_copy(self):
        """Test dirty build of doc copy."""
        simple_test = simple.Simple(**self.default_settings)
        simple_test.include_folders = set(["foo/"])

        # /foo
        #  ├── bar.md

        test_filename = "foo/bar.md"
        self.fs.create_file(test_filename)
        built_filename = "/build_dir/foo/bar.md"

        # Get the modification time of the original file
        src_time = os.path.getmtime(test_filename)

        paths = simple_test.build_docs(dirty=True, last_build_time=0)
        # Check that the file was built
        self.assertIn(test_filename, paths)
        # Check that the output file exists
        self.assertTrue(os.path.exists(built_filename))
        # Get the modification time
        dest_time = os.path.getmtime(built_filename)
        # Check that the time is newer
        self.assertLess(src_time, dest_time)

        # Run again, but this time set the last build time
        paths = simple_test.build_docs(dirty=True, last_build_time=dest_time)
        # Check that the file was not built
        self.assertNotIn(test_filename, paths)
        # Check that the file still exists in the output
        self.assertTrue(os.path.exists(built_filename))
        # Get the modification time
        dirty_time = os.path.getmtime(built_filename)
        # Check that it is the same as the previous
        self.assertEqual(dest_time, dirty_time)

        # Update a fake file
        with open(test_filename, 'w') as f:
            f.write('Modified!')

        paths = simple_test.build_docs(dirty=True, last_build_time=dirty_time)
        # Check that path was built
        self.assertIn(test_filename, paths)
        # Check that destination file exists
        self.assertTrue(os.path.exists(built_filename))
        # Get the modification time
        modified_time = os.path.getmtime(built_filename)
        # Check that the modification time is newer
        self.assertLess(dirty_time, modified_time)

    def test_build_docs_dirty_extract(self):
        """Test dirty build of doc extraction."""
        settings = self.default_settings
        settings["semiliterate"] = [
            {
                'pattern': r'.*'
            }
        ]
        simple_test = simple.Simple(**settings)
        simple_test.include_folders = set(["foo/"])

        # /foo
        #  ├── bar.txt
        test_filename = "foo/bar.txt"
        self.fs.create_file(test_filename, contents="Hello, world!")
        built_filename = "/build_dir/foo/bar.md"

        # Get the modification time of the original file
        src_time = os.path.getmtime(test_filename)

        paths = simple_test.build_docs(dirty=True, last_build_time=0)
        # Check that the file was built
        self.assertIn(test_filename, paths)
        # Check that the output file exists
        self.assertTrue(os.path.exists(built_filename))
        # Get the modification time
        dest_time = os.path.getmtime(built_filename)
        # Check that the time is newer
        self.assertLess(src_time, dest_time)
        with open(built_filename, 'r') as f:
            self.assertEqual(f.read(), "Hello, world!\n")

        # Run again, but this time set the last build time
        paths = simple_test.build_docs(dirty=True, last_build_time=dest_time)
        # Check that the file was not built
        self.assertNotIn(test_filename, paths)
        # Check that the file still exists in the output
        self.assertTrue(os.path.exists(built_filename))
        # Get the modification time
        dirty_time = os.path.getmtime(built_filename)
        # Check that it is the same as the previous
        self.assertEqual(dest_time, dirty_time)
        with open(built_filename, 'r') as f:
            self.assertEqual(f.read(), "Hello, world!\n")

        # Update a fake file
        with open(test_filename, 'w') as f:
            f.write('Modified!')

        paths = simple_test.build_docs(dirty=True, last_build_time=dirty_time)
        # Check that path was built
        self.assertIn(test_filename, paths)
        # Check that destination file exists
        self.assertTrue(os.path.exists(built_filename))
        # Get the modification time
        modified_time = os.path.getmtime(built_filename)
        # Check that the modification time is newer
        self.assertLess(dirty_time, modified_time)
        with open(built_filename, 'r') as f:
            self.assertEqual(f.read(), "Modified!\n")

        # Ensure that the file is getting overwritten
        # Update a fake file
        with open(test_filename, 'w') as f:
            f.write('Second time!')

        paths = simple_test.build_docs(
            dirty=True, last_build_time=modified_time)
        # Check that path was built
        self.assertIn(test_filename, paths)
        # Check that destination file exists
        self.assertTrue(os.path.exists(built_filename))
        # Get the modification time
        second_time = os.path.getmtime(built_filename)
        # Check that the modification time is newer
        self.assertLess(modified_time, second_time)
        with open(built_filename, 'r') as f:
            self.assertEqual(f.read(), "Second time!\n")

    def test_merge_docs_copy(self):
        """Test copy_directory"""
        self.fs.create_file('/test/file.txt')
        simple_test = simple.Simple(**self.default_settings)
        simple_test.merge_docs("/test")
        self.assertTrue(os.path.exists("/build_dir/file.txt"))

    def test_merge_docs_update(self):
        """Test merge with update."""
        simple_test = simple.Simple(**self.default_settings)
        test_filename = "/test/file.txt"
        built_filename = "/build_dir/file.txt"

        # Create a fake file
        os.mkdir("test")
        with open(test_filename, 'w') as f:
            f.write('Hello, World!')

        # Get the modification time of the original file
        src_time = os.path.getmtime(test_filename)

        # Merge the docs directory to copy to built
        simple_test.merge_docs("/test")
        self.assertTrue(os.path.exists(built_filename))

        # Get the modification time of the copied file
        dest_time = os.path.getmtime(built_filename)

        # Copied and modified time should be the same
        self.assertLess(src_time, dest_time)

        # Update a fake file
        with open(test_filename, 'w') as f:
            f.write('Modified!')

        # Get the modification time of the updated file
        updated_src_time = os.path.getmtime(test_filename)

        # Updated and original mod time should not be the same
        self.assertLess(src_time, updated_src_time)

        # Merge the docs directory to copy to built
        simple_test.merge_docs("/test")
        self.assertTrue(os.path.exists(built_filename))

        # Get the modification time of the copied file
        updated_dest_time = os.path.getmtime(built_filename)

        # Original and copied file should not be the same
        self.assertNotEqual(src_time, updated_dest_time)
        # New mod time should be less than copied time
        self.assertLess(updated_src_time, updated_dest_time)

        # Merge the docs without updates
        simple_test.merge_docs("/test")
        self.assertTrue(os.path.exists(built_filename))

        # Get the updated time
        no_update_dest_time = os.path.getmtime(built_filename)
        self.assertLess(updated_dest_time, no_update_dest_time)

        # Test dirty copy no update
        simple_test.merge_docs("/test", dirty=True)
        dirty_dest_time = os.path.getmtime(built_filename)
        self.assertEqual(no_update_dest_time, dirty_dest_time)


if __name__ == '__main__':
    unittest.main()
