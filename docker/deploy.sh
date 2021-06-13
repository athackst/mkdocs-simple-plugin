#!/bin/bash

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

git fetch origin ${INPUT_PUBLISH_BRANCH}:${INPUT_PUBLISH_BRANCH}

if [ -z $DRY_RUN ]; then
    mkdocs gh-deploy -b ${INPUT_PUBLISH_BRANCH}
fi
