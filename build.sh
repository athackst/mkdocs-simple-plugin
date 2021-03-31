#!/bin/bash
set -e
pip install -r requirements.txt
pip install -e .
# md file="build.snippet"
# Building this package requires generating the readme files for the examples.
# 
# ```bash
./examples/gen_readme.py
# ```
# 
# And then using `mkdocs_simple_gen` to generate the site.
# 
# ```bash
mkdocs_simple_gen --build -- --verbose
# ```
# /md
