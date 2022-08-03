#!/bin/bash

git config --global --add safe.directory /github/workspace

mkdocs_simple_gen --config-file ${INPUT_CONFIG:-'mkdocs.yml'}
mkdocs build

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

git fetch origin ${INPUT_PUBLISH_BRANCH} --depth=1

if [ -z $DRY_RUN ]; then
    mike set-default ${INPUT_DEFAULT_VERSION}
    mike deploy -p -u -b ${INPUT_PUBLISH_BRANCH} ${INPUT_VERSION}
fi
