#!/usr/bin/env bats
##
# These are helper variables and functions written in Bash. It's like writing in your Terminal!
# Feel free to optimize these, or even run them in your own Terminal.
#

rootDir=$(pwd)
fixturesDir=${rootDir}/examples

debugger() {
    echo "--- STATUS ---"
    if [ $status -eq 0 ]
    then
        echo "Successful Status Code ($status)"
    else
        echo "Failed Status Code ($status)"
    fi
    echo "--- OUTPUT ---"
    printf '%s\n' "${lines[@]}"
    echo "--------------"
    echo "--- CONFIG ---"
    cat mkdocs.yml
    echo "--------------"
    echo "--- FILES ----"
    pwd
    ls -R
    echo "--------------"
}

assertGen() {
    if [ -f mkdocs-test.yml ]
    then
        cp mkdocs-test.yml mkdocs.yml
    fi
    run mkdocs_simple_gen
    check_site_name
    run mkdocs build --verbose
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

assertParGrep() {
    cat site/$1/index.html | \
        awk '/<div class="col-md-9" role="main">/,/<footer class="col-md-12">/' | \
        sed '1d; $d'  | head -n -3 > site/$1.grepout
    # BANDAID: fix mkdocstrings id order for 3.6/3.7
    sed -i 's/<h3 class="doc doc-heading" id="module.main">/<h3 id="module.main" class="doc doc-heading">/g' site/$1.grepout
    echo "--------------"
    echo "-_---File-----"
    echo `pwd`/site/$1/index.html
    echo "-----Grep results-----"
    run diff --ignore-blank-lines --ignore-all-space $1.grepout site/$1.grepout
    echo "-----Output-----"
    cat site/$1.grepout
    echo "--------------"
    [ "$status" -eq 0 ]
}

check_site_name() {
    site_name=$(cat mkdocs.yml | sed -n 's/site_name: \(.*\)/\1/p')
    directory_name=${PWD##*/}
    echo "mkdocs site_name: $site_name, directory: $directory_name"
    [ "$site_name" == "$directory_name" ]
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
    assertFileExists site/index.html
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

@test "use custom extraction parameters" {
    cd ${fixturesDir}/ok-mkdocs-custom-extract
    assertGen
    assertValidSite
    assertFileExists site/fibo/index.html
    assertParGrep fibo
}

@test "ignore site directory" {
    cd ${fixturesDir}/ok-mkdocs-ignore-site-dir
    assertGen
    cp index.md site/test.md
    mkdocs build -d test_site
    assertFileExists test_site/index.html
    assertFileNotExists test_site/site/test/index.html
    rm -fr test_site
}

@test "build a site extracted from source files" {
    cd ${fixturesDir}/ok-source-extract
    assertGen
    assertValidSite
    assertFileExists site/main/index.html
    assertFileExists site/module/index.html
    assertParGrep main
    assertParGrep module
}

@test "build a site extracted from source with mkdocstrings" {
    cd ${fixturesDir}/ok-with-mkdocstrings
    assertGen
    assertValidSite
    assertFileExists site/module/index.html
    assertParGrep module
}

@test "one-off file rename" {
    cd ${fixturesDir}/ok-with-rename
    assertGen
    assertValidSite
    assertFileExists site/baz/index.html
}

@test "build a site extracted from source with macros" {
    cd ${fixturesDir}/ok-with-macros
    assertGen
    assertValidSite
    assertParGrep module
}

@test "build a site extracted from source with snippet" {
    cd ${fixturesDir}/ok-source-with-snippet
    assertGen
    assertValidSite
    assertParGrep module
    assertParGrep snippet
    assertParGrep snippet2
}

@test "build a site with custom replace" {
    cd ${fixturesDir}/ok-source-replace
    assertGen
    assertValidSite
    assertParGrep module
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
