#!/bin/bash

# Get the directory of the script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"

rm -rf ${DIR}site/
rm -rf ${DIR}docs/
rm -f ${DIR}/mkdocs.yml
