#!/bin/bash

# md file="setup.snippet" content="^#?\s?(.*)"
# You will need to have [MKDocs](https://www.mkdocs.org/) installed on your system.
# I recommend installing it via pip to get the latest version.
# 
# ```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  python-pip \
  libcairo2-dev \
  libfreetype6-dev \
  libffi-dev \
  libjpeg-dev \
  libpng-dev \
  libz-dev

pip install --upgrade pip
pip install --user -r requirements.txt
# ```
# 
# /md
