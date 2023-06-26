#!/bin/bash

# Get the directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"

rm ${DIR}/docs/README.md
rm ${DIR}/docs/test.md
