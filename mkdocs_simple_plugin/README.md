# Development

## Prerequisites

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

## Testing

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
