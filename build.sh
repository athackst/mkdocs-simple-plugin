#!/bin/bash
set -e
pip install -r requirements.txt
pip install -e .
# md file="build.snippet"
# Building this package simply requires using `mkdocs_simple_gen` to generate the site.
# 
# ```bash
mkdocs_simple_gen --build -- --verbose
# ```
# /md
