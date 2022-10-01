#!/bin/bash
VERSION=$(cat VERSION)
docker build -f Dockerfile \
    -t althack/mkdocs-simple-plugin:latest \
    -t althack/mkdocs-simple-plugin:$VERSION .
