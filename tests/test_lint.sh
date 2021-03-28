#!/bin/bash

# Lint via flake8
echo "Running flake8 linter -------->"
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=setup.py
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=80 --statistics --exclude=setup.py

echo "Running pydocstyle"
pydocstyle --count --convention=google --add-ignore=D415,D107 .
