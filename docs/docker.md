# Docker

Rou can use this plugin with the [athackst/mkdocs-simple-plugin](https://hub.docker.com/r/athackst/mkdocs-simple-plugin) docker image.

By using the docker image, you don't need to have the plugin or its dependencies installed on your system.

## Run in a docker container

Install, build and serve your docs:

```bash
docker run --rm -it --network=host -v ${PWD}:/docs --user $(id -u):$(id -g) athackst/mkdocs-simple-plugin
```

Explanation of docker command line options

<!-- markdownlint-disable MD038 -->
| command                    | description                                                                 |
| :------------------------- | :-------------------------------------------------------------------------- |
| `--rm`                     | [optional] remove the docker image after it finishes running.               |
| `-it`                      | [optional] run in an interactive terminal.                                  |
| `-p 8000:8000`             | [required] Map the mkdocs server port to a port on your localhost.          |
| `-v ${PWD}:/docs`          | [required] Mount the local directory into the docs directory to build site. |
| `--user $(id -u):$(id -g)` | [recommended] Run the docker container with the current user and group.     |
<!-- markdownlint-enable MD038 -->

The docker image by default runs `mkdocs serve`.

## Set up an command line alias

Add an alias for the docker command to serve docs from any workspace.

```bash
echo 'function mkdocs_simple() { 
    docker run --rm -it --network=host -v ${PWD}:/docs --user $(id -u):$(id -g) athackst/mkdocs-simple-plugin $@ 
}' >> ~/.bashrc
```
