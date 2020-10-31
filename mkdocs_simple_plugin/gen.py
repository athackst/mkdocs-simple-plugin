import click
import os
import yaml


def default_config():
    config = {}
    config['site_name'] = os.path.basename(os.path.abspath("."))
    if "SITE_NAME" in os.environ.keys():
        config['site_name'] = os.environ["SITE_NAME"]
    if "SITE_URL" in os.environ.keys():
        config['site_url'] = os.environ["SITE_URL"]
    if "REPO_URL" in os.environ.keys():
        config['repo_url'] = os.environ["REPO_URL"]
    config['docs_dir'] = "docs"
    config['plugins'] = ["simple", "search"]
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
    """
    config_file = "mkdocs.yml"
    config = default_config()
    if not os.path.exists(config_file):
        # If config file doesn't exit, create a simple one, guess the site name from the folder name.
        write_config(config_file, config)
    # Open the config file to verify settings.
    with open(config_file, 'r') as stream:
        try:
            local_config = yaml.load(stream, yaml.Loader)
            if local_config:
                if "plugins" in local_config.keys():
                    # Merge plugin lists
                    config_plugins = config["plugins"]
                    local_plugins = local_config["plugins"]
                    [i for i in local_plugins if i not in config_plugins
                        or config_plugins.remove(i)]
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
