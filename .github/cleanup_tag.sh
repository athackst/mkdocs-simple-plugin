#!/bin/bash

if [ -z ${DRY_RUN} ]; then
    echo "Merging changes into main"
    git push origin main
else
    echo "Deleting temporary tags and branches"
    git push --delete origin v${VERSION}
    git push --delete origin release/v${VERSION}
fi
