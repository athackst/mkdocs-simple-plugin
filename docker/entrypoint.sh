#!/bin/bash
set -e

if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

mkdocs_simple_gen
mkdocs build

exec "$@"
