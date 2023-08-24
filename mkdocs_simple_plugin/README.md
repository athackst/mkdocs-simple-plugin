# Package Guide

## Prerequisites

{% include "setup.snippet" %}

## Building

{% include "build.snippet" %}

## Testing
 
{% include "tests/linters.snippet" %}

{% include "tests/unit_tests.snippet" %}

{% include "tests/integration_tests.snippet" %}

{% include "tests/local_tests.snippet" %}

## VSCode

This package includes a preconfigured Visual Studio Code (VSCode) workspace and development container, making it easier to get started with developing your plugin. 

To get started with developing your plugin in VSCode, follow these steps:

1. **Open the project in VSCode** Open VSCode and select the "Open Folder" option from the File menu. Navigate to the location where you've saved the project and select the root folder of the project.

2. **Connect to the development container** VSCode will automatically detect the presence of the development container and prompt you to connect to it. Follow the on-screen instructions to connect to the container.

3. **Run the build task** To build the plugin, you can use the preconfigured build task in VSCode. This task is defined in the `build.sh` file and can be run by using the "Run Build Task" option from the Terminal menu or by using the Ctrl + Shift + B shortcut.

4. **Debug the plugin** You can use the VSCode debugger to inspect the code and debug your plugin. The debugger is configured in the launch.json file and can be started by using the "Start Debugging" option from the Debug menu or by using the F5 key.

For more information on how to use VSCode and Docker for development, please refer to [how I develop with VSCode and Docker](https://allisonthackston.com/articles/docker-development.html) and [how I use VSCode tasks](https://allisonthackston.com/articles/vscode-tasks.html).

## Packaging

The project uses Hatch to build and package the plugin [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)

Hatch is a Python packaging tool that helps simplify the process of building and distributing Python packages. It automates many manual steps, such as creating a setup script, creating a distribution package, and uploading the package to a repository, allowing developers to focus on writing code. Hatch is flexible and customizable, with options for specifying dependencies, including additional files, and setting up test suites, and is actively maintained with a growing community of users and contributors.

### Build the package

```bash
hatch build
```

### Publish the package

```bash
hatch publish
```

Please note that you may need to set up the appropriate credentials for the repository before you can publish the package. If you encounter any issues with publishing the package, please refer to the [Hatch documentation](https://hatch.pypa.io/latest/) for guidance.
