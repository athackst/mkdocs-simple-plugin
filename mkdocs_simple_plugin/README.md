# Developing

## Prerequisites

You will need to have [MKDocs](https://www.mkdocs.org/) installed on your system.  I recommend installing it via pip to get the latest version.

```bash
sudo apt-get install python-pip
pip install --upgrade pip --user
pip install mkdocs --user
```

If you want to run the test suite, you'll also need 'bats'

```bash
sudo apt-get install bats
```

## Local install

Install the package locally with

```bash
pip install -e .
```

## Testing

Testing involves both linting with flake8 with the [script](/tests/test_lint.sh)

```bash
./tests/test_lint.sh
```

and testing with the [script](/tests/test.bats)

```bash
./tests/test.bats
```

If you want to test against all the different versions of python, run the [script](/tests/test_local.sh)

```bash
./tests/test_local.sh
```

## VSCode

Included in this package is a VSCode workspace and development container.  See [how I develop with VSCode and Docker](https://www.allisonthackston.com/articles/docker_development.html) and [how I use VSCode tasks](https://www.allisonthackston.com/articles/vscode_tasks.html).
