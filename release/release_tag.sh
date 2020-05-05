#!/bin/bash
set -e

DIR=`pwd`
cd /tmp
git clone -b master --depth 1 git@github.com:athackst/mkdocs-simple-plugin.git
cd mkdocs-simple-plugin
VERSION=`./release/bump.py $@`
echo "Releasing version ${VERSION}"
git add setup.py
git commit -m "Releasing version v${VERSION}"
git tag "v${VERSION}"
git push origin master
git push --tag
cd $DIR