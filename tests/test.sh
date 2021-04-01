#!/bin/bash
set -e
pip install -r requirements.txt
pip install -e .
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
# #### Manual Testing
# 
# To run manually, first you need to generate the readmes
# 
# ```bash
./examples/gen_readme.py
# ```
# 
# Then run the bats script
# 
# ```bash
./tests/test.bats
# ```
# 
# /md
