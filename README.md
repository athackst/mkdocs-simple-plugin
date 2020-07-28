# mkdocs-simple-plugin

| [Docs](http://athackst.github.io/mkdocs-simple-plugin) | [Code](http://github.com/athackst/mkdocs-simple-plugin)  | [PyPi](https://pypi.org/project/mkdocs-simple-plugin/) | [Docker](https://hub.docker.com/r/athackst/mkdocs-simple-plugin) |

![Test](https://github.com/athackst/mkdocs-simple-plugin/workflows/Test/badge.svg) ![Docs](https://github.com/athackst/mkdocs-simple-plugin/workflows/Docs/badge.svg) ![Docker](https://img.shields.io/docker/pulls/athackst/mkdocs-simple-plugin?color=blue) ![pypi](https://img.shields.io/pypi/dm/mkdocs-simple-plugin?color=blue)

This plugin enables you to build documentation from markdown files interspersed within your code using [mkdocs](https://www.mkdocs.org/).  It is designed for the way developers commonly write documentation in their own code -- with simple markdown files.

## About

You may be wondering why you would want to generate a static site for your project, without doing the typical "wiki" thing of consolidating all documentation within a single `docs` folder or using a single `README` file.

* **My repository is too big for a single documentation source.**

    Sometimes it isn't really feasible to consolidate all documentation within an upper level `docs` directory.  This is often the case with medium/large repositories.  In general, if your code base is too large to fit well within a single `include` directory, your code base is probably also too large for documentation to fit within a single `docs` directory.  

    Since it's typically easier to keep documentation up to date when it lives as close to the code as possible, it is better to create multiple sources for documentation.

* **My repository is too simple for advanced documentation.**

    If your code base is _very very_ large, something like the [monorepo plugin](https://github.com/spotify/mkdocs-monorepo-plugin) might better fit your needs.

    For most other medium+ repositories that have grown over time, you probably have scattered documentation throughout your code.  By combining all of that documentation while keeping folder structure, you can better surface and collaborate with others. And, let's face it.  That documentation is probably all in markdown, since github renders it nicely.

* **I want a pretty documentation site without the hassle.**

    Finally, you may be interested in this plugin if you have a desire for stylized documentation, but don't want to invest the time/energy in replicating information you already have in your README.md files, and you want to keep them where they are (thank you very much).

## Getting Started

This plugin was made to be super simple to use.

Install the plugin with pip.

```bash
pip install mkdocs-simple-plugin
```

_Python 3.x, 3.5, 3.6, 3.7, 3.8 supported._

### Build the docs

It's easy to use this plugin.  You can either use the generation script included, or set up your own custom config.

#### Basic

Basic usage was optimized around ease of use.  Simply run

```bash
mkdocs_simple_gen
```

and you're all set!

See [mkdocs_simple_gen](mkdocs_simple_plugin/README.md#mkdocs_simple_gen) for more info.

#### Advanced

Advanced usage is _also_ easy.

Create a `mkdocs.yml` file in the root of your directory and add this plugin to it's plugin list.

```yaml
site_name: your_site_name
plugins:
  - simple
```

See [mkdocs-simple-plugin](mkdocs_simple_plugin/README.md#mkdocs-simple-plugin) for more info.

Then, you can build the mkdocs from the command line.

```bash
mkdocs build
```

### Run a local server

One of the best parts of mkdocs is it's ability to serve (and update!) your documentation site locally.

```bash
mkdocs serve
```

## Run in a docker container

Additionally, you can use this plugin with the [athackst/mkdocs-simple-plugin](https://hub.docker.com/r/athackst/mkdocs-simple-plugin) docker image.

By using the docker image, you don't need to have the plugin or its dependencies installed on your system.

Install, build and serve your docs:

```bash
docker run --rm -it --network=host -v ${PWD}:/docs --user $(id -u):$(id -g) athackst/mkdocs-simple-plugin
```

Explanation of docker command line options

<!-- markdownlint-disable MD038 -->
| command                    | description                                                                 |
| :------------------------- | :-------------------------------------------------------------------------- |
| `--rm`                     | [optional] remove the docker image after it finishes running.               |
| `-it`                      | [optional] run in an interactive terminal.                                  |
| `-p 8000:8000`             | [required] Map the mkdocs server port to a port on your localhost.          |
| `-v ${PWD}:/docs`          | [required] Mount the local directory into the docs directory to build site. |
| `--user $(id -u):$(id -g)` | [recommended] Run the docker container with the current user and group.     |
<!-- markdownlint-enable MD038 -->

See [mkdocs_simple_gen](mkdocs_simple_plugin/README.md#mkdocs_simple_gen) for a list of command line options you can set.

<!-- markdownlint-disable MD046 -->
!!! tip
    Add an alias for the docker command to serve docs from any workspace.

    ```bash
    echo 'function mkdocs_simple() { 
        docker run --rm -it --network=host -v ${PWD}:/docs --user $(id -u):$(id -g) athackst/mkdocs-simple-plugin $@ 
    }' >> ~/.bashrc
    ```
<!-- markdownlint-enable MD046 -->

## Deploy

### Enable GitHub pages

First, set up your github repository to enable gh-pages support.

See [Github Pages](https://pages.github.com/) for more information.

### Deploy from the command line

Mkdocs includes an easy command to initialize your deployment from the command line. This will set up the gh-pages branch and copy the site over.

```bash
mkdocs gh-deploy
```

Then push the results to your repository (or wherever you'd like to host your site).

### Deploy from GitHub Actions

Create a yaml file with the following contents in the `.github/workflows` directory in your repository

```yaml
name: Docs

on:
  push:
    branches: [master]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v1
        with:
          python-version: "3.x"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      - name: Build Docs
        run: |
          mkdocs_simple_gen
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_branch: gh-pages
          publish_dir: ./site
```

## Build plugin from source

### Prerequisites

You will need to have [mkdocs](https://www.mkdocs.org/) installed on your system.  I recommend installing it via pip to get the latest version.

```bash
sudo apt-get install python-pip
pip install --upgrade pip --user
pip install mkdocs --user
```

If you want to run the test suite, you'll also need 'bats'

```bash
sudo apt-get install bats
```

### Develop

Install the package locally with

```bash
pip install -e .
```

Testing involves both linting with flake8

```bash
./tests/test_flake8.sh
```

and testing with `bats`

```bash
./tests/integration/test.bats
```

If you want to test against all the different versions of python, run the local test script.

```bash
./tests/test_local.sh
```

## License

This software is licensed under [Apache 2.0](https://github.com/athackst/mkdocs-simple-plugin/blob/master/LICENSE)
