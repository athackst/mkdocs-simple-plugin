#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

# Update the VARIANT arg in devcontainer.json to pick a Python version: 3, 3.8, 3.7, 3.6 
# To fully customize the contents of this image, use the following Dockerfile instead:
# https://github.com/microsoft/vscode-dev-containers/tree/v0.112.0/containers/python-3/.devcontainer/base.Dockerfile
ARG VARIANT="3"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

ENV DEBIAN_FRONTEND=noninteractive
ENV GEM_HOME="/usr/local/bundle"
ENV PATH $GEM_HOME/bin:$GEM_HOME/gems/bin:$PATH
RUN apt-get update \
   && apt-get -y install --no-install-recommends bats gcc \
   # Ruby for html-proofer
   && apt-get install -y --no-install-recommends ruby ruby-dev \
   && gem install html-proofer \
   && gem install chef-utils -v 16.6.14 \
   && gem install mdl \
   # git settings
   && apt-get install -y --no-install-recommends wget \
   && wget -O /etc/profile.d/git_aliases.sh https://github.com/athackst/workstation_setup/raw/main/user/.aliases/git_aliases.sh \
   && echo "source /etc/profile.d/git_aliases.sh" >> /home/vscode/.bashrc \
   # Clean up
   && apt-get autoremove -y \
   && apt-get clean -y \
   && rm -rf /var/lib/apt/lists/*
   
ENV DEBIAN_FRONTEND=dialog
