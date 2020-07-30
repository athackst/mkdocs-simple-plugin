import click
import os
import yaml


def default_config():
    config = {}
    config['site_name'] = os.path.basename(os.path.abspath("."))
    config['plugins'] = ["simple"]
    return config


def write_config(config_file, config):
    with open(config_file, 'w+') as stream:
        try:
            yaml.dump(config, stream, sort_keys=False)
        except yaml.YAMLError as exc:
            print(exc)


def get_plugins(config):
    plugins = []
    for item in config["plugins"]:
        if type(item) == dict:
            plugins = plugins + list(item.keys())
        else:
            plugins.append(item)
    return plugins


def setup_config():
    """
    Create all the files, including the mkdocs.yml file if it doesn't exist.
    :return:
    """
    docs_dir = "docs"
    config_file = "mkdocs.yml"
    if not os.path.exists(config_file):
        # If config file doesn't exit, create a simple one, guess the site name from the folder name.
        write_config(config_file, default_config())
    # Open the config file to verify settings.
    with open(config_file, 'r') as stream:
        try:
            config = yaml.load(stream, yaml.Loader)
            if not config:
                # If config is not able to be loaded, replace with default config.
                config = default_config()
                write_config(config_file, config)
            if("plugins" not in config):
                # If no plugins are specified in the config, add the simple plugin
                config["plugins"].append("simple")
                write_config(config_file, config)
            if ("simple" not in get_plugins(config)):
                # If the simple plugin isn't included, add it.
                config["plugins"].append("simple")
                write_config(config_file, config)
            if ("site_name" not in config):
                config['site_name'] = os.path.basename(os.path.abspath("."))
                write_config(config_file, config)
            if ("docs_dir" not in config):
                # If the docs_dir is not specified, check if the default dir exists
                config["docs_dir"] = docs_dir
            if(not os.path.exists(config["docs_dir"])):
                print("making docs_dir {}".format(config["docs_dir"]))
                os.makedirs(config["docs_dir"], exist_ok=True)
        except yaml.YAMLError as exc:
            print(exc)


@click.command()
@click.option('--build/--no-build', default=True, help="build the site using mkdocs build")
@click.argument('build-args', nargs=-1)
def main(build, build_args):
    """
    Generate and build a mkdocs site.

    See mkdocs build -h for additional build args.
    """
    setup_config()
    if build:
        os.system("mkdocs build " + " ".join(build_args))


if __name__ == "__main__":
    # pylint doesn't know how to parse the click decorators, so disable no-value-for-parameter on main
    # pylint: disable=no-value-for-parameter
    main()
