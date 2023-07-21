#!/usr/bin/env bats
##
# These are helper variables and functions written in Bash. It's like writing in your Terminal!
# Feel free to optimize these, or even run them in your own Terminal.
#

rootDir=$(pwd)
fixturesDir=${rootDir}/examples
testDir=''

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
    echo "Cleaning ${testDir}"
    rm -rf ${testDir}/site/
    rm -f ${testDir}/mkdocs.yml
    if [ -f "${testDir}/clean.sh" ]; then
        ${testDir}/clean.sh
    fi
}

##
# Test suites.
#

@test "build an empty mkdocs site with minimal configuration" {
    testDir=${fixturesDir}/ok-empty
    cd ${testDir}
    assertGen
    assertEmptySite
}

@test "build an empty mkdocs site with a config" {
    testDir=${fixturesDir}/ok-mkdocs-config
    cd ${testDir}
    assertGen
    assertEmptySite
}

@test "build a mkdocs site with just a docs folder" {
    testDir=${fixturesDir}/ok-mkdocs-docs
    cd ${testDir}
    assertGen
    assertValidSite
}

@test "build a mkdocs site with just a readme" {
    testDir=${fixturesDir}/ok-mkdocs-readme
    cd ${testDir}
    assertGen
    assertValidSite
}

@test "build a mkdocs site that merges docs folder and other documentation" {
    testDir=${fixturesDir}/ok-mkdocs-docs-merge
    cd ${testDir}
    assertGen
    assertFileExists site/test/index.html
    assertFileExists site/draft/index.html
    assertFileExists site/index.html
    assertFileNotExists site/docs/draft/index.html
    assertFileNotExists site/docs/index.html
}

@test "build a mkdocs site that doesn't merge docs folder and other documentation" {
    testDir=${fixturesDir}/ok-mkdocs-docs-no-merge
    cd ${testDir}
    assertGen
    assertFileExists site/test/index.html
    assertFileNotExists site/draft/index.html
    assertFileExists site/index.html
    assertFileExists site/docs/draft/index.html
    assertFileExists site/docs/index.html
}

@test "build a mkdocs site that specifies a specific folder to include" {
    testDir=${fixturesDir}/ok-mkdocs-docs-include
    cd ${testDir}
    assertGen
    assertFileExists site/subfolder/draft/index.html
    assertFileExists site/subfolder/index.html
}

@test "build a mkdocs site that ignores a specific folder" {
    testDir=${fixturesDir}/ok-mkdocs-docs-ignore
    cd ${testDir}
    assertGen
    assertFileNotExists site/subfolder/index.html
    assertFileNotExists site/subfolder/draft/index.html
    assertFileExists site/test/index.html
}

@test "build a mkdocs site that includes extra extensions" {
    testDir=${fixturesDir}/ok-mkdocs-docs-extensions
    cd ${testDir}
    assertGen
    assertFileExists site/test.txt
}

@test "use custom extraction parameters" {
    testDir=${fixturesDir}/ok-mkdocs-custom-extract
    cd ${testDir}
    assertGen
    assertValidSite
    assertFileExists site/fibo/index.html
    assertParGrep fibo
    assertFileExists site/drone_develop/index.html
    assertParGrep drone_develop
}

@test "ignore site directory" {
    testDir=${fixturesDir}/ok-mkdocs-ignore-site-dir
    cd ${testDir}
    assertGen
    cp index.md site/test.md
    mkdocs build -d test_site
    assertFileExists test_site/index.html
    assertFileNotExists test_site/site/test/index.html
    rm -fr test_site
}

@test "build a site extracted from source files" {
    testDir=${fixturesDir}/ok-source-extract
    cd ${testDir}
    assertGen
    assertValidSite
    assertFileExists site/main/index.html
    assertFileExists site/module/index.html
    assertParGrep main
    assertParGrep module
}

@test "build a site extracted from source with mkdocstrings" {
    testDir=${fixturesDir}/ok-with-mkdocstrings
    cd ${testDir}
    assertGen
    assertValidSite
    assertFileExists site/module/index.html
    assertParGrep module
}

@test "one-off file rename" {
    testDir=${fixturesDir}/ok-with-rename
    cd ${testDir}
    assertGen
    assertValidSite
    assertFileExists site/baz/index.html
}

@test "build a site extracted from source with macros" {
    testDir=${fixturesDir}/ok-with-macros
    cd ${testDir}
    assertGen
    assertValidSite
    assertParGrep example
    assertParGrep module
}

@test "build a site extracted from source with snippet" {
    testDir=${fixturesDir}/ok-source-with-snippet
    cd ${testDir}
    assertGen
    assertValidSite
    assertParGrep module
    assertParGrep snippet
    assertParGrep snippet2
}

@test "build a site with custom replace" {
    testDir=${fixturesDir}/ok-source-replace
    cd ${testDir}
    assertGen
    assertValidSite
    assertParGrep module
}

@test "build a site with inline settings" {
    testDir=${fixturesDir}/ok-mkdocs-inline-settings
    cd ${testDir}
    assertGen
    assertValidSite
    assertParGrep main
}

@test "ignore a file" {
    testDir=${fixturesDir}/ok-mkdocs-ignore-file
    cd ${testDir}
    assertGen
    assertValidSite
    assertFileExists site/test/index.html
    assertFileNotExists site/hello_world/index.html
}

@test "mkdocsignore" {
    testDir=${fixturesDir}/ok-mkdocsignore
    cd ${testDir}
    assertGen
    assertValidSite
    assertFileNotExists site/test/foo/index.html
    assertFileNotExists site/test/bar/index.html
    assertFileExists site/hello/hello/index.html
    assertFileNotExists site/hello/world/world/index.html
    assertFileExists site/hello/foo/bar/index.html
    assertFileNotExists site/hello/foo/foo/index.html
}

@test "serve a mkdocs site" {
    testDir=${fixturesDir}/ok-mkdocs-docs
    cd ${testDir}
    assertGen
    assertValidSite
    mkdocs serve &
    sleep 5
    assertServeSuccess
    pkill mkdocs
}
