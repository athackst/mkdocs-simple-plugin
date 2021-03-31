#!/bin/bash
set -e
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
# ./tests/test.sh
# ```
# 
# /md
pip install -r requirements.txt
pip install -e .
./examples/gen_readme.py
./tests/test.bats
