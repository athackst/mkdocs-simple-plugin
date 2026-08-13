#!/usr/bin/env python
"""Test mkdocs_simple_plugin.plugin."""
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files

from mkdocs_simple_plugin.plugin import SimplePlugin, get_config_site_dir


class TestSimplePlugin(unittest.TestCase):
    """Test SimplePlugin configuration."""

    def make_plugin(self, config=None):
        """Create a configured plugin and clean up its temporary directory."""
        plugin = SimplePlugin()
        self.addCleanup(
            shutil.rmtree, plugin.tmp_build_dir, ignore_errors=True)
        errors, warnings = plugin.load_config(config or {})
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        return plugin

    def make_mkdocs_config(self, root):
        """Create a valid MkDocs configuration rooted in a test directory."""
        docs_dir = root / "docs"
        site_dir = root / "site"
        docs_dir.mkdir()

        config = MkDocsConfig()
        config.load_dict({
            "site_name": "Test site",
            "docs_dir": str(docs_dir),
            "site_dir": str(site_dir),
        })
        errors, warnings = config.validate()
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        return config

    def test_default_include_preserves_navigation_files(self):
        """Test default navigation files are copied into generated docs."""
        plugin = self.make_plugin()

        self.assertIn(".pages", plugin.config["include"])
        self.assertIn(".nav.yml", plugin.config["include"])

    def test_on_startup_records_dirty_mode(self):
        """Test startup passes the dirty-build state to file generation."""
        plugin = self.make_plugin()

        plugin.on_startup(command="serve", dirty=True)

        self.assertTrue(plugin.dirty)

    def test_on_config_merges_into_docs_directory(self):
        """Test the default configuration builds into the docs directory."""
        plugin = self.make_plugin()
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        config = self.make_mkdocs_config(Path(temporary_directory.name))
        docs_dir = os.path.abspath(config["docs_dir"])
        site_dir = os.path.abspath(config["site_dir"])

        with patch(
                "mkdocs_simple_plugin.plugin.get_config_site_dir",
                return_value=site_dir):
            result = plugin.on_config(config)

        self.assertIs(config, result)
        self.assertEqual(docs_dir, plugin.orig_docs_dir)
        self.assertEqual(docs_dir, plugin.config["build_dir"])
        self.assertEqual(docs_dir, config["docs_dir"])
        self.assertIn(".nav.yml", plugin.config["include"])
        self.assertIn(docs_dir, plugin.config["ignore_paths"])
        self.assertIn(site_dir, plugin.config["ignore_paths"])
        self.assertIn("include:", config["mkdocs_simple_config"])

    def test_on_config_uses_temporary_directory_without_merge(self):
        """Test disabling merge switches MkDocs to the temporary directory."""
        plugin = self.make_plugin({"merge_docs_dir": False})
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        config = self.make_mkdocs_config(Path(temporary_directory.name))
        original_docs_dir = config["docs_dir"]

        with patch(
                "mkdocs_simple_plugin.plugin.get_config_site_dir",
                return_value=config["site_dir"]):
            plugin.on_config(config)

        self.assertEqual(original_docs_dir, plugin.orig_docs_dir)
        self.assertEqual(plugin.tmp_build_dir, plugin.config["build_dir"])
        self.assertEqual(plugin.tmp_build_dir, config["docs_dir"])

    def test_on_files_replaces_existing_file_with_generated_file(self):
        """Test generated documentation replaces the original MkDocs file."""
        plugin = self.make_plugin()
        plugin.dirty = True
        plugin.last_build_time = 10
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)
        config = self.make_mkdocs_config(root)
        output_root = root / "generated"
        output_root.mkdir()
        generated_path = SimpleNamespace(
            input_path=str(root / "README.md"),
            output_root=str(output_root),
            output_relpath="README.md",
        )
        original = File(
            path="README.md",
            src_dir=config["docs_dir"],
            dest_dir=config["site_dir"],
            use_directory_urls=config["use_directory_urls"],
        )
        files = Files([original])

        with patch("mkdocs_simple_plugin.plugin.Simple") as simple_class, \
                patch("mkdocs_simple_plugin.plugin.time.time",
                      return_value=20):
            simple_class.return_value.build_docs.return_value = [
                generated_path]
            result = plugin.on_files(files, config=config)

        simple_class.assert_called_once_with(**plugin.config)
        simple_class.return_value.build_docs.assert_called_once_with(
            True, 10, False)
        self.assertIs(files, result)
        self.assertEqual(20, plugin.last_build_time)
        self.assertEqual(1, len(files))
        generated = files.get_file_from_path("README.md")
        self.assertEqual("mkdocs_simple_plugin", generated.generated_by)
        self.assertEqual(str(output_root), generated.src_dir)

    def test_on_files_removes_original_docs_without_merge(self):
        """Test non-merge mode removes MkDocs' original docs files."""
        plugin = self.make_plugin({"merge_docs_dir": False})
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)
        config = self.make_mkdocs_config(root)
        original = File(
            path="original.md",
            src_dir=config["docs_dir"],
            dest_dir=config["site_dir"],
            use_directory_urls=config["use_directory_urls"],
        )
        files = Files([original])

        with patch("mkdocs_simple_plugin.plugin.Simple") as simple_class:
            simple_class.return_value.build_docs.return_value = []
            plugin.on_files(files, config=config)

        self.assertEqual(0, len(files))

    def test_on_serve_updates_watched_paths(self):
        """Test serve ignores generated files and watches their sources."""
        plugin = self.make_plugin({"build_dir": "/tmp/generated-docs"})
        plugin.paths = [
            SimpleNamespace(input_path="README.md"),
            SimpleNamespace(input_path="docs/guide.md"),
        ]
        server = MagicMock()
        server._watched_paths = {plugin.config["build_dir"]: None}

        result = plugin.on_serve(
            server, config=MagicMock(), builder=MagicMock())

        self.assertIs(server, result)
        server.unwatch.assert_called_once_with(plugin.config["build_dir"])
        server.watch.assert_any_call("README.md")
        server.watch.assert_any_call("docs/guide.md")
        self.assertEqual(2, server.watch.call_count)

    def test_get_config_site_dir_reads_original_configuration(self):
        """Test the configured site directory is resolved from mkdocs.yml."""
        temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        root = Path(temporary_directory.name)
        (root / "docs").mkdir()
        config_path = root / "mkdocs.yml"
        config_path.write_text(
            "site_name: Test site\n"
            "docs_dir: docs\n"
            "site_dir: output\n",
            encoding="utf-8",
        )

        result = get_config_site_dir(str(config_path))

        self.assertEqual(str(root / "output"), result)


if __name__ == "__main__":
    unittest.main()
