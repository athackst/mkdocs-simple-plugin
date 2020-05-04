#!/bin/bash

set -e

git checkout master
git pull
export VERSION=`./release/bump.py $@`
echo "Releasing version ${VERSION}"
git add setup.py
git commit -m "Releasing version ${VERSION}"
git push origin master
git tag "v${VERSION}"
git push --tags
exit 0