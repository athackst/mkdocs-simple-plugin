from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs import config as mkdocs_config
from mkdocs import utils

import fnmatch
import os
import shutil
import sys
import tempfile


def common_extensions():
    return [".bmp", ".tif", ".tiff", ".gif", ".svg", ".jpeg", ".jpg", ".jif", ".jfif",
            ".jp2", ".jpx", ".j2k", ".j2c", ".fpx", ".pcd", ".png", ".pdf", "CNAME"]


def get_config_site_dir(config_file_path):
    orig_config = mkdocs_config.load_config(config_file_path)
    utils.log.debug(
        "mkdocs-simple-plugin: loading file: {}".format(config_file_path))

    utils.log.debug(
        "mkdocs-simple-plugin: User config site_dir: {}".format(orig_config.data['site_dir']))
    return orig_config.data['site_dir']


class SimplePlugin(BasePlugin):
    """ SimplePlugin adds documentation throughout your repo to a mkdocs wiki.

    Usage:

        site_name: your_site_name
        plugins:
        - simple:
            # Optional setting to only include specific folders
            include_folders: ["*"]
            # Optional setting to ignore specific folders
            ignore_folders: [""]
            # Optional setting to specify if hidden folders should be ignored
            ignore_hidden: True
            # Optional setting to specify other extensions besides md files to be copied
            include_extensions: eval(common_extensions())
            # Optional setting to merge the docs directory with other documentation
            merge_docs_dir: True
    """
    config_scheme = (
        ('include_folders', config_options.Type(list, default=['*'])),
        ('ignore_folders', config_options.Type(list, default=[])),
        ('ignore_hidden', config_options.Type(bool, default=True)),
        ('include_extensions', config_options.Type(
            list, default=common_extensions())),
        ('merge_docs_dir', config_options.Type(bool, default=True))
    )

    def on_pre_build(self, config, **kwargs):
        self.include_folders = self.config['include_folders']
        self.ignore_folders = self.config['ignore_folders']
        self.ignore_hidden = self.config['ignore_hidden']
        self.include_extensions = utils.markdown_extensions + \
            self.config['include_extensions']
        self.merge_docs_dir = self.config['merge_docs_dir']
        # The temp folder to dump all the documentation
        self.build_docs_dir = os.path.join(
            tempfile.gettempdir(),
            'mkdocs-simple',
            os.path.basename(os.getcwd()),
            "docs_")
        # # Always ignore the output paths
        self.ignore_paths = [get_config_site_dir(config.config_file_path),
                             config['site_dir'],
                             self.build_docs_dir]
        # Save original docs directory location
        self.orig_docs_dir = config['docs_dir']
        # Copy contents of docs directory if merging
        if self.merge_docs_dir and os.path.exists(self.orig_docs_dir):
            self.copy_docs_dir(self.orig_docs_dir, self.build_docs_dir)
            self.ignore_paths += [self.orig_docs_dir]
        # Copy all of the valid doc files into build_docs_dir
        self.paths = self.copy_doc_files(self.build_docs_dir)
        # Update the docs_dir with our temporary one
        config['docs_dir'] = self.build_docs_dir

    def on_serve(self, server, config, **kwargs):
        builder = list(server.watcher._tasks.values())[0]['func']

        # still watch the original docs/ directory
        if os.path.exists(self.orig_docs_dir):
            server.watch(self.orig_docs_dir, builder)

        # watch all the doc files
        for orig, _ in self.paths:
            server.watch(orig, builder)

        return server

    def on_post_build(self, config, **kwargs):
        shutil.rmtree(self.build_docs_dir)

    def in_search_dir(self, dir, root):
        if self.ignore_hidden and dir[0] == ".":
            return False
        if any(fnmatch.fnmatch(dir, filter) for filter in self.ignore_folders):
            return False
        if os.path.abspath(os.path.join(root, dir)) in self.ignore_paths:
            return False
        return True

    def in_include_dir(self, dir):
        return any(fnmatch.fnmatch(dir, filter) for filter in self.include_folders)

    def in_extensions(self, file):
        return any(extension in file for extension in self.include_extensions)

    def copy_doc_files(self, dest_dir):
        paths = []
        for root, dirs, files in os.walk("."):
            if self.in_include_dir(root):
                for f in files:
                    if self.in_extensions(f):
                        doc_root = dest_dir + root[1:]
                        orig = "{}/{}".format(root, f)
                        new = "{}/{}".format(doc_root, f)
                        try:
                            os.makedirs(doc_root, exist_ok=True)
                            shutil.copy(orig, new)
                            utils.log.debug(
                                "mkdocs-simple-plugin: {} --> {}".format(orig, new))
                            paths.append((orig, new))
                        except Exception as e:
                            utils.log.warn(
                                "mkdocs-simple-plugin: error! {}.. skipping {}".format(e, orig))

            dirs[:] = [d for d in dirs if self.in_search_dir(d, root)]
        return paths

    def copy_docs_dir(self, root_src_dir, root_dst_dir):
        if(sys.version_info >= (3, 8)):
            # pylint: disable=unexpected-keyword-arg
            shutil.copytree(root_src_dir, root_dst_dir, dirs_exist_ok=True)
            utils.log.debug(
                "mkdocs-simple-plugin: {}/* --> {}/*".format(root_src_dir, root_dst_dir))
        else:
            for src_dir, _, files in os.walk(root_src_dir):
                dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                for file_ in files:
                    src_file = os.path.join(src_dir, file_)
                    dst_file = os.path.join(dst_dir, file_)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    shutil.copy(src_file, dst_dir)
                    utils.log.debug(
                        "mkdocs-simple-plugin: {}/* --> {}/*".format(src_file, dst_file))
