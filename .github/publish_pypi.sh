#!/bin/bash

# Builds and uploads the python package
# Environment variables:
#   TWINE_USERNAME: pypi username
#   TWINE_PASSWORD: pypi password
#   DRY_RUN: <bool>

python -m pip install --upgrade pip
pip install setuptools wheel twine
if [ -f requirements.txt ]; then
    pip install -r requirements.txt;
fi
python setup.py sdist bdist_wheel

if [ -z ${DRY_RUN} ]; then
    twine upload dist/* --verbose
fi
