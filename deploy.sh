#!/bin/bash

git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"

git fetch origin ${BRANCH_NAME}:${BRANCH_NAME}

mkdocs gh-deploy -b ${BRANCH_NAME}
