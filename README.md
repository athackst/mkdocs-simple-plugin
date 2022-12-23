![mkdocs-simple-plugin](https://github.com/athackst/mkdocs-simple-plugin/raw/main/media/mkdocs-simple-plugin.png)

[![Test](https://github.com/athackst/mkdocs-simple-plugin/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/athackst/mkdocs-simple-plugin/actions/workflows/test.yml)
[![Docs](https://github.com/athackst/mkdocs-simple-plugin/actions/workflows/publish_docs.yml/badge.svg?branch=main)](https://github.com/athackst/mkdocs-simple-plugin/actions/workflows/publish_docs.yml)
[![Docker](https://img.shields.io/docker/pulls/althack/mkdocs-simple-plugin)](https://hub.docker.com/r/althack/mkdocs-simple-plugin)
[![pypi](https://img.shields.io/pypi/dm/mkdocs-simple-plugin?label=pypi%20downloads&color=blue)](https://pypi.org/project/mkdocs-simple-plugin/)
[![Github Action](https://img.shields.io/badge/github%20action-download-blue)](https://github.com/marketplace/actions/mkdocs-simple-action)

# mkdocs-simple-plugin

This plugin enables you to build a documentation site from markdown interspersed within your repository using [mkdocs](https://www.mkdocs.org/).

## About

You may be wondering why you would want to generate a static site for your project without doing the typical "wiki" thing of consolidating all documentation within a single `docs` folder or using a single `README` file.

* **My repository is too big for a single documentation source.**

    Sometimes it isn't feasible to consolidate all documentation within an upper level `docs` directory.  In general, if your codebase is too large to fit well within a single `include` directory, your codebase is also too large for documentation in a single `docs` directory.

    Since it's typically easier to keep documentation up to date when it lives as close to the code as possible, it is better to create multiple sources for documentation.

* **My repository is too simple for advanced documentation.**

    If your codebase is _very very_ large, something like the [monorepo plugin](https://github.com/spotify/mkdocs-monorepo-plugin) might better fit your needs.

    For most other medium+ repositories that have grown over time, you probably have scattered documentation throughout your code.  By combining all of that documentation while keeping folder structure, you can better surface and collaborate with others. And, let's face it.  That documentation is probably all in markdown since Github renders it nicely.

* **I want a pretty documentation site without the hassle.**

    Finally, you may be interested in this plugin if you have a desire for easy-to-generate stylized documentation.  This plugin lets you take documentation you may already have -- either in markdown files or in your code -- and formats them into a searchable documentation website.  You can keep your documentation where it is (thank you very much).

See [mkdocs-simple-plugin](https://althack.dev/mkdocs-simple-plugin/latest/mkdocs_simple_plugin/plugin) for usage.

## Contributing

See the [contributing guide](https://althack.dev/mkdocs-simple-plugin/latest/CONTRIBUTING)

## License

This software is licensed under [Apache 2.0](https://althack.dev/mkdocs-simple-plugin/latest/LICENSE)
