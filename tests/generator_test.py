#!/usr/bin/env python
"""Test mkdocs_simple_plugin.generator"""
import unittest
import os
import tempfile

from mkdocs import config
from mkdocs import theme
from mkdocs.config import defaults

from mkdocs_simple_plugin import generator


class TestDefaultConfig(unittest.TestCase):
    """Test default configuration with settings."""
    test_mkdocs_filename = os.path.join(
        tempfile.gettempdir(),
        'mkdocs-simple/mkdocs.yml')

    env_variables = [
        'SITE_NAME',
        'SITE_URL',
        'REPO_URL',
        'GOOGLE_ANALYTICS',
        'THEME']

    def setUp(self):
        """Set up the tests by reseting the environment variables."""
        for var in self.env_variables:
            os.unsetenv(var)

    def tearDown(self):
        """Tear down the test by cleaning up temp mkdocs.yml."""
        if os.path.exists(self.test_mkdocs_filename):
            os.remove(self.test_mkdocs_filename)

    def _test_env_setting(
            self,
            env_variable,
            env_value,
            config_name,
            config_value,
            loaded_type=None):
        os.environ[env_variable] = env_value
        test_config = generator.setup_config(self.test_mkdocs_filename)
        self.assertTrue(test_config[config_name])
        self.assertEqual(test_config[config_name], config_value)

        cfg = config.Config(schema=defaults.DEFAULT_SCHEMA)
        cfg.load_dict(test_config)
        errors, warnings = cfg.validate()
        self.assertEqual(len(errors), 0, errors)
        self.assertEqual(len(warnings), 0, warnings)
        if loaded_type:
            self.assertIsInstance(cfg[config_name], loaded_type)
        else:
            self.assertEqual(cfg[config_name], config_value)

    def test_default(self):
        """Test the default configuration without any additional options."""
        test_config = generator.setup_config(self.test_mkdocs_filename)
        cfg = config.Config(schema=defaults.DEFAULT_SCHEMA)
        cfg.load_dict(test_config)
        errors, warnings = cfg.validate()
        self.assertEqual(len(errors), 0, errors)
        self.assertEqual(len(warnings), 0, warnings)

    def test_empty(self):
        """Test the default settings with empty environment variables."""
        for var in self.env_variables:
            os.environ[var] = ""
        self.test_default()

    def test_site_name(self):
        """Test setting the site name."""
        self._test_env_setting(
            env_variable="SITE_NAME",
            env_value="test",
            config_name="site_name",
            config_value="test")

    def test_site_url(self):
        """Test setting the site url."""
        self._test_env_setting(
            env_variable="SITE_URL",
            env_value="https://athackst.github.io/mkdocs-simple-plugin",
            config_name="site_url",
            config_value="https://athackst.github.io/mkdocs-simple-plugin")

    def test_repo_url(self):
        """Test setting the repo url."""
        self._test_env_setting(
            env_variable="REPO_URL",
            env_value="https://github.com/athackst/mkdocs-simple-plugin",
            config_name="repo_url",
            config_value="https://github.com/athackst/mkdocs-simple-plugin")

    def test_google_analytics(self):
        """Test setting google analytics.

        This setting requires at least two items in the list.
        """
        self._test_env_setting(
            env_variable="GOOGLE_ANALYTICS",
            env_value="UA-XXXXXX",
            config_name="google_analytics",
            config_value=["UA-XXXXXX", "auto"])

    def test_theme(self):
        """Test setting the theme.

        mkdocs config changes the type to a Theme object.
        """
        self._test_env_setting(
            env_variable="THEME",
            env_value="material",
            config_name="theme",
            config_value={"name": "material"},
            loaded_type=theme.Theme)


if __name__ == '__main__':
    unittest.main()
