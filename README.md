# athackst/mkdocs-simple-plugin

This plugin enables you to build documentation from markdown files interspersed within your code.  It is designed for the way developers commonly write documentation in their own code -- with simple markdown files.

## About

You may be wondering why you would want to generate a static site for your project, without doing the typical "wiki" thing of consolidating all documentation within a `docs` folder.

1. My repository is too big for a single file

    Sometimes it isn't really feasible to consolidate all documentation within an upper level `docs` directory.  This is often the case with medium/large repositories.  In general, if your code base is too large to fit well within a single `include` directory, your code base is probably also too large for documentation to fit within a single `docs` directory.  

    Since it's typically easier to keep documentation up to date when it lives as close to the code as possible, it is better to create multiple sources for documentation.

2. My repository is too simple for advanced documentation

    If your code base is _very very_ large, something like the [monorepo plugin](https://github.com/spotify/mkdocs-monorepo-plugin) might better fit your needs.

    For most other medium+ repositories that have grown over time, you probably have scattered documentation throughout your code.  By combining all of that documentation while keeping folder structure, you can better surface and collaborate with others. And, let's face it.  That documentation is probably all in markdown, since github renders it nicely.

3. I want a pretty documentation site without the hassle.

    Finally, you may be interested in this plugin if you have a desire for stylized documentation, but don't want to invest the time/energy in replicating information you already have in your README.md files, and you want to keep them where they are (thank you very much).

## Getting Started

This plugin was made to be super simple to use.

### Prerequisites 

You will need to have [mkdocs](https://www.mkdocs.org/) installed on your system.  I recommend installing it via pip to get the latest version.

```bash
sudo apt-get install python-pip
pip install --upgrade pip --user
pip install mkdocs --user
```

### Installation

Then, install the plugin.

```bash
pip install mkdocs-simple-plugin
```

### Usage

It's easy to use this plugin.  You can either use the generation script included, or set up your own custom config.

#### Basic

Basic usage was optimized around ease of use.  Simply run

```bash
mkdocs_simple_gen
```
and you're all set!

#### Advanced

Advanced usage is _also_ easy.

Simply create a `mkdocs.yml` file in the root of your directory and add this plugin to it's plugin list

```yaml
site_name: your_site_name
plugins:
  - simple
```

If you'd like, you can specify some additional configuration settings

```yaml
# simple plugin configuration options
ignore_hidden: True # Ignore md files in hidden directories (those starting with a '.')
ignore_directories: # Folders that should be ignored to add md files
  - "drafts"
```

**Note**

* Files in the `docs_dir` (by default `docs`) will be merged with any other documentation in your repository.
* If you have specified `nav` elements in your mkdocs.yml, only those pages will be rendered in the site

Then, you build the mkdocs from the command line

```bash
mkdocs build
```

### Test

And you can even preview the resulting site

```bash
mkdocs serve
```

### Deploy

TODO
<!--TODO github integration -->

## License

This software is licensed under [Apache 2.0](LICENSE)

## Contributing
