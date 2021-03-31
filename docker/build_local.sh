#!/bin/bash
VERSION=$(cat VERSION)
docker build -f Dockerfile \
    -t athackst/mkdocs-simple-plugin:latest \
    -t athackst/mkdocs-simple-plugin:$VERSION .
