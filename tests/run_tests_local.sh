#!/bin/bash
# md file="test.snippet" content="^#?\s?(.*)"
# ### Different Python versions
# 
# You can even test the package with different versions of python in a container
# by running the test_local script.  This builds a docker container with the 
# version of python you specify and runs the integration tests within the 
# container. 
# 
# ```bash
# ./tests/test_local.sh
# ```
# {% include "versions.snippet" %}
# 
# <details>
# <summary>Code</summary>
#
# ```bash
set -e

# End-to-end testing via Bats (Bash automated tests)
function docker_run_integration_tests() {
docker build -t mkdocs-simple-test-runner:$1 -f- . <<EOF
  FROM python:$1
  RUN apt-get -y update && apt-get -y install bats gcc sudo
  COPY . /workspace
  WORKDIR /workspace
EOF

echo "Running E2E tests via Bats in Docker (python:$1) -------->"
docker run --rm -it mkdocs-simple-test-runner:$1 tests/run_unit_tests.sh
docker run --rm -it mkdocs-simple-test-runner:$1 tests/run_linters.sh
docker run --rm -it mkdocs-simple-test-runner:$1 tests/run_integration_tests.sh
}

if [[ ! -z "$PYTHON_V_ONLY" ]]; then
  echo "only v $PYTHON_V_ONLY"
  docker_run_integration_tests "$PYTHON_V_ONLY"
else
  docker_run_integration_tests "3"
  docker_run_integration_tests "3.7"
  docker_run_integration_tests "3.8"
  docker_run_integration_tests "3.9"
  docker_run_integration_tests "3.10"
fi
# ```
# </details>
# /md
