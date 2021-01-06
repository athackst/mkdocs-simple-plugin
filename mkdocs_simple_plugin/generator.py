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

_Python 3.x, 3.6, 3.7, 3.8, 3.9 supported._

## Usage

```bash
mkdocs_simple_gen
```

### Command line options

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
mkdocs_simple_gen --build --no-serve
```
"""
import click
import tempfile
import os
import yaml


def default_config():
    """Get default configuration for mkdocs.yml file."""
    config = {}
    config['site_name'] = os.path.basename(os.path.abspath("."))
    if "SITE_NAME" in os.environ.keys():
        config['site_name'] = os.environ["SITE_NAME"]
    if "SITE_URL" in os.environ.keys():
        config['site_url'] = os.environ["SITE_URL"]
    if "REPO_URL" in os.environ.keys():
        config['repo_url'] = os.environ["REPO_URL"]
    # Set the docs dir to temporary directory, or docs if the folder exists
    config['docs_dir'] = os.path.join(
        tempfile.gettempdir(),
        'mkdocs-simple',
        os.path.basename(os.getcwd()),
        "docs")
    if os.path.exists(os.path.join(os.getcwd(), "docs")):
        config['docs_dir'] = "docs"
    config['plugins'] = ("simple", "search")
    return config


class MkdocsConfigDumper(yaml.Dumper):
    """Format yaml files better."""

    def increase_indent(self, flow=False, indentless=False):
        """Indent lists."""
        return super(MkdocsConfigDumper, self).increase_indent(flow, False)


def write_config(config_file, config):
    """Write configuration file."""
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


def setup_config():
    """Create the mkdocs.yml file with defaults for params that don't exist."""
    config_file = "mkdocs.yml"
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
    write_config(config_file, config)


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


if __name__ == "__main__":
    # pylint doesn't know how to parse the click decorators,
    # so disable no-value-for-parameter on main
    # pylint: disable=no-value-for-parameter
    main(['--help'])
