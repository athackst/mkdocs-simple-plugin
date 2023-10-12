#!/bin/bash

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  bats \
  gcc \
  ruby \
  ruby-dev

sudo gem install html-proofer

./setup.sh

pip install --user .
