# Docker

Use this image to create a [mkdocs](https://www.mkdocs.org/) site with the [mkdocs-simple-plugin](https://www.althack.dev/mkdocs-simple-plugin)

Using the docker image, you don't need to have the plugin or its dependencies installed on your system to build, test, and deploy a mkdocs generated site.

## Run in a docker container

Install, build and serve your docs:

```bash
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs althack/mkdocs-simple-plugin:latest
```

Explanation of docker command-line options

<!-- markdownlint-disable MD038 -->
| command                    | description                                                                 |
| :------------------------- | :-------------------------------------------------------------------------- |
| `-p 8000:8000`             | [required] Map the mkdocs server port to a port on your localhost.          |
| `-v ${PWD}:/docs`          | [required] Mount the local directory into the docs directory to build site. |
| `--rm`                     | [optional] remove the docker image after it finishes running.               |
| `-it`                      | [optional] run in an interactive terminal.                                  |
<!-- markdownlint-enable MD038 -->

The docker image runs `mkdocs serve` by default.

## Set up a command-line alias

Add an alias for the docker command to serve docs from any workspace.

```bash
echo 'function mkdocs_simple_serve() { 
    local port=${1:-"8000"}
    docker run --rm -it -p ${port}:8000 -v ${PWD}:/docs althack/mkdocs-simple-plugin:latest
}' >> ~/.bashrc
```
