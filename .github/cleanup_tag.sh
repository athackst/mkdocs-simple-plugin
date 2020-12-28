#!/bin/bash

if [ -z ${DRY_RUN} ]; then
    git push origin main
else
    git push --delete origin v${VERSION}
    git push --delete origin release/v${VERSION}
fi
