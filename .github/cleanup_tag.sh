#!/bin/bash

if [ ${DRY_RUN} ]; then
    git push --delete origin v${VERSION}
    git push --delete origin release/v${VERSION}
else
    git push origin main
fi
