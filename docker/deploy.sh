#!/bin/bash
set -e

UNSET='\033[0m'
RED='\033[00;31m'
GREEN='\033[00;32m'
YELLOW='\033[00;33m'
CYAN='\033[00;36m'

git config --global --add safe.directory /github/workspace

echo -e "${CYAN}Building docs${UNSET}"
mkdocs_simple_gen --config-file ${INPUT_CONFIG}

if [[ "${INPUT_PUSH}" == "1" || "${INPUT_PUSH,,}" == "true" ]]; then
    git config --global user.name "${GITHUB_ACTOR}"
    git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"
   
    git fetch origin ${INPUT_PUBLISH_BRANCH} --depth=1 || echo -e "${YELLOW}skipping fetch${UNSET}"

    if [ "${INPUT_VERSION}" ]; then
        echo -e "${CYAN}Deploying ${INPUT_VERSION} to ${INPUT_PUBLISH_BRANCH}${UNSET}"
        mike deploy --config-file ${INPUT_CONFIG} -p -u -b ${INPUT_PUBLISH_BRANCH} ${INPUT_VERSION}
    else
        echo -e "${CYAN}Deploying docs to ${INPUT_PUBLISH_BRANCH}${UNSET}"
        mkdocs gh-deploy --config-file ${INPUT_CONFIG} -b ${INPUT_PUBLISH_BRANCH} 
    fi

    if [ "${INPUT_DEFAULT_VERSION}" ]; then 
        echo -e "${CYAN}Setting default version to ${INPUT_DEFAULT_VERSION}${UNSET}"
        mike set-default -p -b ${INPUT_PUBLISH_BRANCH} ${INPUT_DEFAULT_VERSION}
    fi
else 
    mkdocs build --config-file ${INPUT_CONFIG}
fi
