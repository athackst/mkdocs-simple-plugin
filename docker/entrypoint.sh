#!/bin/bash
set -e

git config --global --add safe.directory /docs

if [ -f "requirements.txt" ]; then
  if [ "$UID" -eq 0 ]; then
    pip install -r requirements.txt
  else
    pip install --user -r requirements.txt
  fi
fi

exec "$@"
