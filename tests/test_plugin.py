#!/usr/bin/env python
"""Test mkdocs_simple_plugin.plugin."""
import unittest

from mkdocs_simple_plugin.plugin import SimplePlugin


class TestSimplePlugin(unittest.TestCase):
    """Test SimplePlugin configuration."""

    def test_default_include_preserves_navigation_files(self):
        """Test default navigation files are copied into generated docs."""
        plugin = SimplePlugin()
        plugin.load_config({})

        self.assertIn(".pages", plugin.config["include"])
        self.assertIn(".nav.yml", plugin.config["include"])


if __name__ == "__main__":
    unittest.main()
