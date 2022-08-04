#!/bin/bash

git config --global --add safe.directory /github/workspace

echo "Building docs"
mkdocs_simple_gen --config-file ${INPUT_CONFIG:-'mkdocs.yml'}
mkdocs build

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

git fetch origin ${INPUT_PUBLISH_BRANCH} --depth=1

if [ ${INPUT_PUSH} ]; then
    mike deploy -p -u -b ${INPUT_PUBLISH_BRANCH} ${INPUT_VERSION}
    echo "Deploying ${INPUT_VERSION} to ${INPUT_PUBLISH_BRANCH}"

    if [ ${INPUT_DEFAULT_VERSION} ]; then 
        mike set-default -p -b ${INPUT_PUBLISH_BRANCH} ${INPUT_DEFAULT_VERSION}
        echo "Setting default version to ${INPUT_DEFAULT_VERSION}"
    fi
fi
