#!/usr/bin/env bats

##
# Install the mkdocs-simple-plugin locally on test run.
#
pip install -e . --quiet >&2

##
# These are helper variables and functions written in Bash. It's like writing in your Terminal!
# Feel free to optimize these, or even run them in your own Terminal.
#

rootDir=$(pwd)
fixturesDir=${rootDir}/tests/integration/fixtures

debugger() {
  echo "--- STATUS ---"
  if [ $status -eq 0 ]
  then
    echo "Successful Status Code ($status)"
  else
    echo "Failed Status Code ($status)"
  fi
  echo "--- OUTPUT ---"
  echo $output
  echo "--------------"
}

assertFileExists() {
  run cat $1
  [ "$status" -eq 0 ]
}

assertFileNotExists() {
  run cat $1
  [ "$status" -ne 0 ]
}

assertGenSuccess() {
  run mkdocs_simple_gen
  debugger
  [ "$status" -eq 0 ]
  assertFileExists site/index.html
}

assertGenEmpty() {
  run mkdocs_simple_gen
  debugger
  [ "$status" -eq 0 ]
  assertFileNotExists site/index.html
}

assertServeSuccess() {
  run pgrep -x mkdocs
  [ ! -z "$status" ]
}

##
# These are special life cycle methods for Bats (Bash automated testing).
# setup() is ran before every test, teardown() is ran after every test.
#

teardown() {
  for dir in ${fixturesDir}/*; do (cd "$dir" && ./clean.sh); done
}

##
# Test suites.
#

@test "build an empty mkdocs site with minimal configuration" {
  cd ${fixturesDir}/ok-empty
  assertGenEmpty
}

@test "build an empty mkdocs site with a config" {
  cd ${fixturesDir}/ok-mkdocs-config
  assertGenEmpty
}

@test "build a mkdocs site with just a docs folder" {
  cd ${fixturesDir}/ok-mkdocs-docs
  assertGenSuccess
}

@test "build a mkdocs site with just a readme" {
  cd ${fixturesDir}/ok-mkdocs-readme
  assertGenSuccess
}

@test "build a mkdocs site that merges docs folder and other documentation" {
  cd ${fixturesDir}/ok-mkdocs-docs-merge
  assertGenSuccess
  assertFileExists site/test/index.html
  # TODO: check that drafts isn't in nav
}

@test "serve a mkdocs site" {
  cd ${fixturesDir}/ok-mkdocs-docs
  mkdocs_simple_gen --serve &
  sleep 5
  assertServeSuccess
  pkill mkdocs
}