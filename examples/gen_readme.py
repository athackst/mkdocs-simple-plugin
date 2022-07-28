#!/usr/bin/env python3
"""Generate the dockerfiles from a jinja template."""
import os
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
import yaml


log = logging.getLogger(__name__)


class DisplayablePath(object):
    """Utility to print file folders as a tree."""
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        """Make the tree as a path."""
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @ classmethod
    def _default_criteria(cls, path):
        """Default criteria includes everything."""
        return True

    @ property
    def displayname(self):
        """Pretty format the file name."""
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        """Get the name with tree prefixes."""
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


class GenerateExampleReadme():
    """Generate example radme for a folder."""

    def __init__(self, readme_template):
        self.readme_template = readme_template
        self.home_dir = os.getcwd()

    def include_input(self, path):
        """The files to expand as input examples."""
        include_list = ['.py', '.c', '.litcoffee', '.cpp']
        return any(extension in path.displayname for extension in include_list)

    def include_output(self, path):
        """The files to expand as output examples."""
        include_list = ['.grepout']
        return any(extension in path.displayname for extension in include_list)

    def get_file_info(self, path):
        """Returns a dictionary of file properties."""
        return {
            # get the name
            "name": path.displayname,
            # get the type
            "type": path.path.suffix,
            # get the path
            "path": str(path.path),
            # get stem of file name
            "stem": path.path.stem
        }

    def create(self, title, folder):
        """Create the readme file."""
        log.info("Generating readme for %s", folder)
        # mkdocs_config
        mkdocs_config = os.path.join(folder, "mkdocs-test.yml")
        # input tree
        display_tree = []
        input_files = []
        output_files = []
        os.system(f"cp {folder}/mkdocs-test.yml {folder}/mkdocs.yml")

        # Get input tree
        def input_criteria(path):
            """The files to include in the input."""
            ignore_list = ['site', 'mkdocs-test.yml', '__pycache__']
            return not any(extension in path.name for extension in ignore_list)
        paths = DisplayablePath.make_tree(
            Path(folder), criteria=input_criteria)
        for path in paths:
            # get all of the grepouts
            if self.include_output(path):
                output_files.append(self.get_file_info(path))
                continue
            # get the source files
            if self.include_input(path):
                input_files.append(self.get_file_info(path))
            # create the tree
            display_tree.append(path.displayable())
        input_tree = "\n".join(display_tree)

        # run mkdocs_simple_gen
        os.chdir(folder)
        os.system("mkdocs_simple_gen --build")
        os.chdir(self.home_dir)

        # output tree
        display_tree = []
        site_folder = os.path.join(folder, "site/")

        def output_criteria(path):
            """The files to include in the output."""
            ignore_list = ['css', 'fonts', 'img', 'js', 'search', "xml", "404"]
            return not any(extension in path.name for extension in ignore_list)
        paths = DisplayablePath.make_tree(
            Path(site_folder), criteria=output_criteria)
        for path in paths:
            display_tree.append(path.displayable())
        output_tree = "\n".join(display_tree)

        # write the readme
        readme_output = self.readme_template.render(
            {
                "title": title,
                "mkdocs_config": mkdocs_config,
                "input_tree": input_tree,
                "input_files": input_files,
                "output_tree": output_tree,
                "output_files": output_files
            }
        )
        readme_file = folder + "/README.md"
        readme_out = open(readme_file, "w")
        readme_out.write(readme_output)
        readme_out.close()

        # cleanup
        os.system(f"rm -rf {folder}/site {folder}/mkdocs.yml")


def generate(*args, **kwargs):
    """Generate all of the readmes"""
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)

    def include_file(name):
        """Function to help includes without applying further macros."""
        return Markup(file_loader.get_source(env, name)[0])
    env.globals['include_file'] = include_file
    readme_template = env.get_template('examples/README.md.jinja')

    # Load .pages for titles and filenames
    with open("examples/.pages", 'r') as stream:
        try:
            example_docs = yaml.load(stream, yaml.Loader)
        except yaml.YAMLError as exc:
            print(exc)
            raise

    for item in example_docs["nav"]:
        for title, folder in item.items():
            GenerateExampleReadme(readme_template).create(title, folder)


if __name__ == "__main__":
    generate()
