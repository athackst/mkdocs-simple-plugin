"""md

# Mkdocs Simple Generator

`mkdocs_simple_gen` is a program that will automatically create a `mkdocs.yml`
configuration file (only if needed) and optionally install dependencies, build,
and serve the site.

# Installation

Install the plugin with pip.

```bash
pip install mkdocs-simple-plugin
```

{% include "versions.snippet" %}

"""
import click
import tempfile
import os
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

    if "CONFIG_FILE" in os.environ.keys() and os.environ["CONFIG_FILE"]:
        with open(os.environ["CONFIG_FILE"], 'r') as file:
            try:
                config = yaml.load(file)
            except yaml.YAMLError as exc:
                print(exc)

    config['site_url'] = 'http://localhost'

    # Set the config variables via environment if exist
    if "SITE_NAME" in os.environ.keys() and os.environ["SITE_NAME"]:
        config['site_name'] = os.environ["SITE_NAME"]
    if "SITE_URL" in os.environ.keys() and os.environ["SITE_URL"]:
        config['site_url'] = os.environ["SITE_URL"]
    if "SITE_DIR" in os.environ.keys() and os.environ["SITE_DIR"]:
        config['site_dir'] = os.environ["SITE_DIR"]
    if "REPO_URL" in os.environ.keys() and os.environ["REPO_URL"]:
        config['repo_url'] = os.environ["REPO_URL"]
    if "THEME" in os.environ.keys() and os.environ["THEME"]:
        config['theme'] = {'name': os.environ["THEME"]}
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
                print("making docs_dir {}".format(config["docs_dir"]))
                os.makedirs(config["docs_dir"], exist_ok=True)

        except yaml.YAMLError as exc:
            print(exc)
            raise
    print(config_file)
    write_config(config_file, config)
    return config


@click.command()
@click.option('--build/--no-build', default=False,
              help="build the site using mkdocs build")
@click.option('--serve/--no-serve', default=False,
              help="serve the site using mkdocs serve")
@click.argument('mkdocs-args', nargs=-1)
def main(build, serve, mkdocs_args):
    """Generate and build a mkdocs site."""
    setup_config()
    if build:
        os.system("mkdocs build " + " ".join(mkdocs_args))
    if serve:
        os.system("mkdocs serve " + " ".join(mkdocs_args))


""" md
# Usage

```bash
mkdocs_simple_gen
```

# Command line options

See `--help`

```txt
Usage: mkdocs_simple_gen [OPTIONS]

Options:
  --build / --no-build      build the site using mkdocs build
  --serve / --no-serve      serve the site using mkdocs serve
  --help                    Show this message and exit.
```

default flags:

```bash
mkdocs_simple_gen --no-build --no-serve
```
"""
if __name__ == "__main__":
    # pylint doesn't know how to parse the click decorators,
    # so disable no-value-for-parameter on main
    # pylint: disable=no-value-for-parameter
    main(['--help'])
