#!/usr/bin/env python
"""Test mkdocs_simple_plugin.generator"""
import unittest
import os
import tempfile

from mkdocs import theme
from mkdocs.config import defaults
import yaml

from mkdocs_simple_plugin import generator


class TestDefaultConfig(unittest.TestCase):
    """Test default configuration with settings."""
    test_mkdocs_filename = os.path.join(
        tempfile.gettempdir(),
        'mkdocs-simple/mkdocs.yml')

    env_variables = [
        'INPUT_SITE_NAME',
        'INPUT_SITE_URL',
        'INPUT_REPO_URL',
        'INPUT_THEME',
        'DEFAULT_SITE_NAME',
        'DEFAULT_SITE_URL',
        'DEFAULT_REPO_URL',
        'DEFAULT_THEME']

    def setUp(self):
        """Set up the tests by resetting the environment variables."""
        for var in self.env_variables:
            if os.environ.get(var) is not None:
                del os.environ[var]

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
        os.environ["INPUT_"+env_variable] = env_value
        test_config = generator.setup_config(self.test_mkdocs_filename)
        self.assertTrue(test_config[config_name])
        self.assertEqual(test_config[config_name], config_value)

        cfg = defaults.MkDocsConfig()
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
        cfg = defaults.MkDocsConfig()
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
            env_value="https://www.althack.dev/mkdocs-simple-plugin/",
            config_name="site_url",
            config_value="https://www.althack.dev/mkdocs-simple-plugin/")

    def test_repo_url(self):
        """Test setting the repo url."""
        self._test_env_setting(
            env_variable="REPO_URL",
            env_value="https://github.com/athackst/mkdocs-simple-plugin",
            config_name="repo_url",
            config_value="https://github.com/athackst/mkdocs-simple-plugin")

    def test_theme(self):
        """Test setting the theme.

        mkdocs config changes the type to a Theme object.
        """
        self._test_env_setting(
            env_variable="THEME",
            env_value="readthedocs",
            config_name="theme",
            config_value={"name": "readthedocs"},
            loaded_type=theme.Theme)

    def test_existing_site_name_is_overwritten_by_env(self):
        """Test that an existing site name is overridden by input."""
        os.environ["INPUT_SITE_NAME"] = "from-env"
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(test_config["site_name"], "from-env")
        with open(self.test_mkdocs_filename, 'r', encoding="utf-8") as stream:
            written_config = yaml.load(stream, yaml.Loader)
        self.assertEqual(written_config["site_name"], "from-env")

    def test_existing_site_url_is_overwritten_by_env(self):
        """Test that an existing site url is overridden by input."""
        os.environ["INPUT_SITE_URL"] = "https://example.com/from-env/"
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "site_url": "https://example.com/from-file/",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(
            test_config["site_url"],
            "https://example.com/from-env/")
        with open(self.test_mkdocs_filename, 'r', encoding="utf-8") as stream:
            written_config = yaml.load(stream, yaml.Loader)
        self.assertEqual(
            written_config["site_url"],
            "https://example.com/from-env/")

    def test_existing_site_url_is_preserved_without_env(self):
        """Test that an existing site url is preserved without input."""
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "site_url": "https://example.com/from-file/",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(
            test_config["site_url"],
            "https://example.com/from-file/")

    def test_existing_site_url_is_preserved_with_empty_env(self):
        """Test that an empty site url input does not override."""
        os.environ["INPUT_SITE_URL"] = ""
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "site_url": "https://example.com/from-file/",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(
            test_config["site_url"],
            "https://example.com/from-file/")

    def test_action_default_site_url_is_used_without_file_setting(self):
        """Test that action default site url is used when missing."""
        os.environ["DEFAULT_SITE_URL"] = (
            "https://example.com/from-action/")
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(
            test_config["site_url"],
            "https://example.com/from-action/")

    def test_action_default_site_url_does_not_overwrite_file_setting(self):
        """Test that action default site url does not override config."""
        os.environ["DEFAULT_SITE_URL"] = (
            "https://example.com/from-action/")
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "site_url": "https://example.com/from-file/",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(
            test_config["site_url"],
            "https://example.com/from-file/")

    def test_input_site_url_overwrites_action_default_and_file_setting(self):
        """Test that input site url overrides action default and config."""
        os.environ["INPUT_SITE_URL"] = "https://example.com/from-input/"
        os.environ["DEFAULT_SITE_URL"] = (
            "https://example.com/from-action/")
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "site_url": "https://example.com/from-file/",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(
            test_config["site_url"],
            "https://example.com/from-input/")

    def test_existing_theme_is_overwritten_by_env(self):
        """Test that an existing theme is overridden by input."""
        os.environ["INPUT_THEME"] = "readthedocs"
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
                "theme": {"name": "mkdocs"},
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(test_config["theme"], {"name": "readthedocs"})
        cfg = defaults.MkDocsConfig()
        cfg.load_dict(test_config)
        errors, warnings = cfg.validate()
        self.assertEqual(len(errors), 0, errors)
        self.assertEqual(len(warnings), 0, warnings)
        self.assertIsInstance(cfg["theme"], theme.Theme)

    def test_existing_theme_is_preserved_without_env(self):
        """Test that an existing theme is preserved without input."""
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
                "theme": {"name": "mkdocs"},
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(test_config["theme"], {"name": "mkdocs"})
        cfg = defaults.MkDocsConfig()
        cfg.load_dict(test_config)
        errors, warnings = cfg.validate()
        self.assertEqual(len(errors), 0, errors)
        self.assertEqual(len(warnings), 0, warnings)
        self.assertIsInstance(cfg["theme"], theme.Theme)

    def test_existing_theme_is_preserved_with_empty_env(self):
        """Test that an empty theme input does not override."""
        os.environ["INPUT_THEME"] = ""
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
                "theme": {"name": "mkdocs"},
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(test_config["theme"], {"name": "mkdocs"})
        cfg = defaults.MkDocsConfig()
        cfg.load_dict(test_config)
        errors, warnings = cfg.validate()
        self.assertEqual(len(errors), 0, errors)
        self.assertEqual(len(warnings), 0, warnings)
        self.assertIsInstance(cfg["theme"], theme.Theme)

    def test_action_default_theme_is_used_without_file_setting(self):
        """Test that action default theme is used when missing."""
        os.environ["DEFAULT_THEME"] = "material"
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(test_config["theme"], {"name": "material"})

    def test_action_default_theme_does_not_overwrite_file_setting(self):
        """Test that action default theme does not override config."""
        os.environ["DEFAULT_THEME"] = "material"
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
                "theme": {"name": "mkdocs"},
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(test_config["theme"], {"name": "mkdocs"})

    def test_input_theme_overwrites_action_default_and_file_setting(self):
        """Test that input theme overrides action default and config."""
        os.environ["INPUT_THEME"] = "readthedocs"
        os.environ["DEFAULT_THEME"] = "material"
        generator.write_config(
            self.test_mkdocs_filename,
            {
                "site_name": "from-file",
                "docs_dir": tempfile.mkdtemp(),
                "plugins": ("simple", "search"),
                "edit_uri": "",
                "theme": {"name": "mkdocs"},
            })

        test_config = generator.setup_config(self.test_mkdocs_filename)

        self.assertEqual(test_config["theme"], {"name": "readthedocs"})


if __name__ == '__main__':
    unittest.main()
