#!/bin/bash
set -e
pip install -e .
./examples/gen_readme.py
./tests/test_lint.sh
./tests/test.bats
