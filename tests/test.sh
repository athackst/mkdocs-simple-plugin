#!/bin/bash
set -e
./tests/run_unit_tests.sh
./tests/run_integration_tests.sh
./tests/run_linters.sh
