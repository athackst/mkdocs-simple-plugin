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

assertGen() {
  run mkdocs_simple_gen --build
  debugger
  [ "$status" -eq 0 ]
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
  assertGen
  assertFileExists site/index.html
}

assertGenEmpty() {
  assertGen
  assertFileNotExists site/index.html
}

assertServeSuccess() {
  run pgrep -x mkdocs
  debugger
  [ ! -z "$status" ]
}

##
# These are special life cycle methods for Bats (Bash automated testing).
# setup() is ran before every test, teardown() is ran after every test.
#

teardown() {
  for dir in ${fixturesDir}/*; do (cd "$dir" && ./clean.sh); done
  rm -fr /tmp/mkdocs
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

@test "build a mkdocs site that specifies a specific folder to include" {
  cd ${fixturesDir}/ok-mkdocs-docs-include
  assertGenEmpty
  assertFileExists site/subfolder/draft/index.html
  assertFileExists site/subfolder/index.html
}

@test "build a mkdocs site that ignores a specific folder" {
  cd ${fixturesDir}/ok-mkdocs-docs-ignore
  assertGenSuccess
  assertFileNotExists site/subfolder/index.html
  assertFileNotExists site/subfolder/draft/index.html
  assertFileExists site/test/index.html
}

@test "build a mkdocs site that includes extra extensions" {
  cd ${fixturesDir}/ok-mkdocs-docs-extensions
  assertGenSuccess
  assertFileExists site/test.txt
}

@test "serve a mkdocs site" {
  cd ${fixturesDir}/ok-mkdocs-docs
  mkdocs_simple_gen --serve &
  sleep 5
  assertServeSuccess
  pkill mkdocs
}
