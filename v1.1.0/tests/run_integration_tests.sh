#!/bin/bash
set -e
sudo apt-get install bats
pip install -e .
pip install mkdocs-macros-plugin mkdocstrings
# md file="test.snippet"
# ### Integration tests
# 
# Integration testing allows the plugin to be tested with mkdocs using example
# configurations.
# 
# Integration testing uses bats, install it with
# 
# ```bash
# sudo apt-get install bats
# ```
# Then run the tests
# 
# ```bash
# ./tests/run_integration_tests.sh
# ```
# <details>
# <summary>Code</summary>
#
# ```bash
./examples/gen_readme.py
./tests/test.bats
# ```
# </details>
# /md
