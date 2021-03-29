#!/bin/bash
set -e
pip install -e .
./examples/gen_readme.py
mkdocs_simple_gen
mkdocs build --verbose
