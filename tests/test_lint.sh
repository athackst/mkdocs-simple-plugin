#!/bin/bash
# md file="test.snippet"
# ### Lint
# 
# Linting helps maintain style consistency.  This package follows the [google 
# style guide](https://google.github.io/styleguide/pyguide.html).  Conformity
# is enforced with flake8 and pydodstyle.
# 
# ```bash
# ./tests/test_lint.sh
# ```
# 
# /md

# Lint via flake8
echo "Running flake8 linter -------->"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=setup.py
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=80 --statistics --exclude=setup.py

echo "Running pydocstyle"
pydocstyle --count --convention=google --add-ignore=D415,D107 .
