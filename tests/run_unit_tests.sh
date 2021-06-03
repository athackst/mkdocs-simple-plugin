#!/bin/bash
set -e
pip install -r requirements.txt
pip install -e .
# md file="test.snippet"
# ### Unit tests
#
# Unit tests help ensure individual functions perform as expected.  Unit tests
# in this module use the the standard python unittest framework.
#
# ```bash
# ./tests/run_unit_tests.sh
# ```
#
# <details>
# <summary>Code</summary>
# ```bash
python3 -m unittest tests/*_test.py
# ```
# </details>
# /md
