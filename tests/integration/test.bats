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
    echo "--- CONFIG ---"
    cat mkdocs.yml
    echo "--------------"
    echo "--- FILES ----"
    ls -R
    echo "--------------"
}

assertGen() {
    if [ -f mkdocs-test.yml ]
    then
        cp mkdocs-test.yml mkdocs.yml
    fi
    run mkdocs_simple_gen
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

assertValidSite() {
    assertFileExists site/index.html
}

assertEmptySite() {
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
    for dir in ${fixturesDir}/*
    do
        rm -rf ${dir}/site/
        rm -rf ${dir}/docs_/
        rm -f mkdocs.yml
    done
}

##
# Test suites.
#

@test "build an empty mkdocs site with minimal configuration" {
    cd ${fixturesDir}/ok-empty
    assertGen
    assertEmptySite
}

@test "build an empty mkdocs site with a config" {
    cd ${fixturesDir}/ok-mkdocs-config
    assertGen
    assertEmptySite
}

@test "build a mkdocs site with just a docs folder" {
    cd ${fixturesDir}/ok-mkdocs-docs
    assertGen
    assertValidSite
}

@test "build a mkdocs site with just a readme" {
    cd ${fixturesDir}/ok-mkdocs-readme
    assertGen
    assertValidSite
}

@test "build a mkdocs site that merges docs folder and other documentation" {
    cd ${fixturesDir}/ok-mkdocs-docs-merge
    assertGen
    assertFileExists site/test/index.html
    assertFileExists site/draft/index.html
    assertFileExists site/index.html
    assertFileNotExists site/docs/draft/index.html
    assertFileNotExists site/docs/index.html
}

@test "build a mkdocs site that doesn't merge docs folder and other documentation" {
    cd ${fixturesDir}/ok-mkdocs-docs-no-merge
    assertGen
    assertFileExists site/test/index.html
    assertFileNotExists site/draft/index.html
    assertFileNotExists site/index.html
    assertFileExists site/docs/draft/index.html
    assertFileExists site/docs/index.html
}

@test "build a mkdocs site that specifies a specific folder to include" {
    cd ${fixturesDir}/ok-mkdocs-docs-include
    assertGen
    assertFileExists site/subfolder/draft/index.html
    assertFileExists site/subfolder/index.html
}

@test "build a mkdocs site that ignores a specific folder" {
    cd ${fixturesDir}/ok-mkdocs-docs-ignore
    assertGen
    assertFileNotExists site/subfolder/index.html
    assertFileNotExists site/subfolder/draft/index.html
    assertFileExists site/test/index.html
}

@test "build a mkdocs site that includes extra extensions" {
    cd ${fixturesDir}/ok-mkdocs-docs-extensions
    assertGen
    assertFileExists site/test.txt
}

@test "serve a mkdocs site" {
    cd ${fixturesDir}/ok-mkdocs-docs
    assertGen
    assertValidSite
    mkdocs serve &
    sleep 5
    assertServeSuccess
    pkill mkdocs
}
