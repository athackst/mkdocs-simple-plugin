import click
import os
import yaml


def default_config():
    config = {}
    config['site_name'] = os.path.basename(os.path.abspath("."))
    config['plugins'] = ["simple"]
    return config


def write_config(config_file, config):
    with open(config_file, 'w') as stream:
        try:
            yaml.dump(config, stream)
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
    config_file = "./mkdocs.yml"
    if not os.path.exists(config_file):
        # If config file doesn't exit, create a simple one, guess the site name from the folder name.
        write_config(config_file, default_config())
    else:
        # Otherwise, open the config file to verify settings.
        with open(config_file, 'r') as stream:
            try:
                config = yaml.safe_load(stream)
                if not config:
                    config = default_config()
                    write_config(config_file, config)
                elif("plugins" not in config):
                    config["plugins"].append("simple")
                    write_config(config_file, config)
                elif ("simple" not in get_plugins(config)):
                    config["plugins"].append("simple")
                    write_config(config_file, config)
                if("docs_dir" in config):
                    docs_dir = config["docs_dir"]
            except yaml.YAMLError as exc:
                print(exc)

    # Make the docs_dir if it doesn't already exist.
    if(not os.path.exists(docs_dir)):
        os.makedirs(docs_dir, exist_ok=True)


def install_modules():
    """
    Install modules in requirements.txt
    :param modules: str - List of modules to install
    :return:
    """
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(requirements_file, " doesn't exist -- skip installing modules")
        return
    os.system("pip install -r " + requirements_file)


@click.command()
@click.option('--build/--no-build', default=True, help="build the site using mkdocs build")
@click.option('--install/--no-install', default=False, help="install required packages listed in requirements.txt")
@click.option('--serve/--no-serve', default=False, help="serve the site locally")
@click.option('--dev-addr', help="Local server address", default="127.0.0.1:8000", type=str)
def main(build, install, serve, dev_addr):
    if install:
        install_modules()
    setup_config()
    if build:
        os.system('mkdocs build')
    if serve:
        os.system('mkdocs serve --dev-addr='+ dev_addr)


if __name__ == "__main__":
    main()
