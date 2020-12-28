#!/bin/bash

echo "Bumping version to ${VERSION}"
sed "s/^    version=.*/    version='${VERSION}',/" -i setup.py
git checkout -b release/v${VERSION}
git add setup.py
git commit -m "releasing v${VERSION}"
echo "Update tag and push"
git tag --force "v${VERSION}"
git push --force origin v${VERSION}
git push --force origin release/v${VERSION}
