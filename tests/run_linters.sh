#!/bin/bash
set -e
pip install flake8 pydocstyle
# md file="test.snippet" content="^#?\s?(.*)"
# ### Lint
# 
# Linting helps maintain style consistency.  This package follows the [google 
# style guide](https://google.github.io/styleguide/pyguide.html).  Conformity
# is enforced with flake8 and pydodstyle.
# 
# ```bash
# ./tests/run_linters.sh
# ```
# 
# <details>
# <summary>Code</summary>
#
# ```bash
echo "Running flake8 linter -------->"
flake8 --count .

echo "Running pydocstyle"
pydocstyle --count .
# ```
# </details>
# /md
