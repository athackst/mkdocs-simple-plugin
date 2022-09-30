#!/usr/bin/env python
"""Test mkdocs_simple_plugin.simple"""
import unittest
from unittest.mock import patch
import stat
import os
from pyfakefs.fake_filesystem_unittest import TestCase

from mkdocs_simple_plugin import simple


class TestSimpleHelpers(TestCase):
    """Test Simple helper functions."""

    def setUp(self):
        """Set up with fake filesystem"""
        self.setUpPyfakefs()

    def test_copy_directory(self):
        """Test copy_directory"""
        self.fs.create_file('/test/file.txt')
        simple.copy_directory("/test", '/bar')
        self.assertTrue(os.path.exists("/bar/file.txt"))


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
    def test_is_hidden(self, os_stat):
        """Test is_hidden for correctness."""
        simple_test = simple.Simple(**self.default_settings)
        simple_test.ignore_hidden = True
        os_stat.return_value.st_file_attributes = 0
        self.assertFalse(simple_test.is_hidden('test.md'))
        self.assertFalse(simple_test.is_hidden('./folder/test.md'))
        self.assertTrue(simple_test.is_hidden('__pycache__'))
        self.assertTrue(simple_test.is_hidden('.mkdocsignore'))
        self.assertTrue(simple_test.is_hidden(".git/objects/34/49807110bdc8"))
        # Check hidden file attribute
        os_stat.return_value.st_file_attributes = stat.FILE_ATTRIBUTE_HIDDEN
        self.assertTrue(simple_test.is_hidden('/test/file'))

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
        #  ├── .mkdocsignore
        #  └── bar
        #      ├── spam.md // ignored
        #      ├── hello.txt
        #      └── eggs.md
        #  └── bat
        #      ├── hello.md
        #      └── world.md
        # /goo
        #  └── day.md
        # boo.md
        self.fs.create_file("/foo/baz.md")
        self.fs.create_file("/foo/.mkdocsignore", contents="bar/spam.md*")
        self.fs.create_file("/foo/bar/spam.md")
        self.fs.create_file("/foo/bar/hello.txt")
        self.fs.create_file("/foo/bar/eggs.md")
        self.fs.create_file("/foo/bat/hello.md")
        self.fs.create_file("/foo/bat/world.md")
        self.fs.create_file("/goo/day.md")
        self.fs.create_file("boo.md")

        files = simple_test.get_files()
        self.assertIn("foo/baz.md", files)
        self.assertIn("foo/.mkdocsignore", files)
        self.assertIn("foo/bar/hello.txt", files)
        self.assertIn("foo/bar/eggs.md", files)
        self.assertNotIn("foo/bar/spam.md", files)
        self.assertIn("foo/bat/hello.md", files)
        self.assertIn("foo/bat/world.md", files)
        self.assertIn("goo/day.md", files)
        self.assertIn("boo.md", files)
        self.assertEqual(8, len(files))

    def test_build_docs(self):
        """Test build docs."""
        simple_test = simple.Simple(**self.default_settings)

        # /foo
        #  ├── baz.md
        #  ├── .mkdocsignore //hidden + ignore settings
        #  ├── .pages //include in copy
        #  └── bar
        #      ├── spam.md // ignored
        #      ├── hello.txt  // wrong extension
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


if __name__ == '__main__':
    unittest.main()
