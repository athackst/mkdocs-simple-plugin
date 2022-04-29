"""md

# Mkdocs Simple Generator

`mkdocs_simple_gen` is a program that will automatically create a `mkdocs.yml`
configuration file (only if needed) and optionally install dependencies, build,
and serve the site.

## Installation

Install the plugin with pip.

```bash
pip install mkdocs-simple-plugin
```

{% include "versions.snippet" %}

## CLI Reference

::: mkdocs-click
    :module: mkdocs_simple_plugin.generator
    :command: main
    :prog_name: mkdocs_simple_gen
    :depth: 2

"""
import os
import tempfile

import click
import yaml


def default_config():
    """Get default configuration for mkdocs.yml file."""
    config = {}
    config['site_name'] = os.path.basename(os.path.abspath("."))
    # Set the docs dir to temporary directory, or docs if the folder exists
    default_docs = os.path.join(os.getcwd(), "docs")
    temp_docs = os.path.join(
        tempfile.gettempdir(),
        'mkdocs-simple',
        os.path.basename(
            os.getcwd()),
        "docs")
    config['docs_dir'] = default_docs if os.path.exists(
        default_docs) else temp_docs

    config['plugins'] = ("simple", "search")

    # Set the default edit uri to empty since doc files are built from source
    # and may not exist.
    config['edit_uri'] = ''

    config['site_url'] = 'http://localhost'

    def maybe_set_string(name):
        env_variable = "INPUT_" + name.upper()
        config_variable = name.lower()
        if os.environ.get(env_variable):
            config[config_variable] = os.environ[env_variable]

    def maybe_set_dict(name, key):
        env_variable = "INPUT_" + name.upper()
        config_variable = name.lower()
        if os.environ.get(env_variable):
            config[config_variable] = {key: os.environ[env_variable]}
    # Set the config variables via environment if exist
    maybe_set_string("site_name")
    maybe_set_string("site_url")
    maybe_set_string("site_dir")
    maybe_set_string("repo_url")
    maybe_set_dict("theme", "name")
    return config


class MkdocsConfigDumper(yaml.Dumper):
    """Format yaml files better."""

    def increase_indent(self, flow=False, indentless=False):
        """Indent lists."""
        return super(MkdocsConfigDumper, self).increase_indent(flow, False)


def write_config(config_file, config):
    """Write configuration file."""
    if os.path.dirname(config_file):
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w+') as file:
        try:
            yaml.dump(
                data=config,
                stream=file,
                sort_keys=False,
                default_flow_style=False,
                Dumper=MkdocsConfigDumper)
        except yaml.YAMLError as exc:
            print(exc)


def setup_config(config_file="mkdocs.yml"):
    """Create the mkdocs.yml file with defaults for params that don't exist."""
    config = default_config()
    if not os.path.exists(config_file):
        # If config file doesn't exit, create a simple one, guess the site name
        # from the folder name.
        write_config(config_file, config)
    # Open the config file to verify settings.
    with open(config_file, 'r') as stream:
        try:
            local_config = yaml.load(stream, yaml.Loader)
            if local_config:
                # Overwrite default config values with local mkdocs.yml
                config.update(local_config)
                print(config)
            if not os.path.exists(config["docs_dir"]):
                #  Ensure docs directory exists.
                print("making docs_dir %s", config["docs_dir"])
                os.makedirs(config["docs_dir"], exist_ok=True)

        except yaml.YAMLError as exc:
            print(exc)
            raise
    write_config(config_file, config)
    return config


@click.command()
@click.option("--config-file", default="mkdocs.yml",
              help="Set the configuration file.")
@click.option('--build/--no-build', default=False,
              help="Build the site using mkdocs build.")
@click.option('--serve/--no-serve', default=False,
              help="Serve the site using mkdocs serve.")
@click.argument('mkdocs-args', nargs=-1)
def main(config_file, build, serve, mkdocs_args):
    """Generate and build a mkdocs site."""
    setup_config(config_file)
    args = mkdocs_args + ("-f", config_file)
    if build:
        os.system("mkdocs build " + " ".join(args))
    if serve:
        os.system("mkdocs serve " + " ".join(args))


if __name__ == "__main__":
    # pylint doesn't know how to parse the click decorators,
    # so disable no-value-for-parameter on main
    # pylint: disable=no-value-for-parameter
    main(['--help'])
