#!/bin/bash
set -e

git config --global --add safe.directory /docs

PIP_OPTS=''

if [ "$UID" -ne 0 ]; then
  PIP_OPTS="--user"
fi

pip install ${PIP_OPTS} --upgrade pip
pip install ${PIP_OPTS} /opt/mkdocs-simple-plugin
pip install ${PIP_OPTS} -r /opt/mkdocs-simple-plugin/requirements.txt

if [ -f "requirements.txt" ]; then
    pip install ${PIP_OPTS} -r requirements.txt
fi

exec "$@"
