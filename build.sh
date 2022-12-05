#!/bin/bash
set -e
pip install -e .
# md file="build.snippet" content="^#?\s?(.*)"
# Building this package requires  using `mkdocs_simple_gen` to generate the site.
# ```bash
mkdocs_simple_gen --build -- --verbose
# ```
# /md
