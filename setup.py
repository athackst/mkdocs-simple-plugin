import setuptools

with open("mkdocs_simple_plugin/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='mkdocs-simple-plugin',
    version='0.1.8',
    description='Plugin for adding simple wiki site creation from markdown files interspersed within your code with MkDocs.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='mkdocs readme wiki',
    url='http://athackst.github.io/mkdocs-simple-plugin',
    project_urls={
        "Issues": "https://github.com/athackst/mkdocs-simple-plugin/issues",
        "Documentation": "http://athackst.github.io/mkdocs-simple-plugin",
        "Source Code": "https://github.com/athackst/mkdocs-simple-plugin",
    },
    author='Allison Thackston',
    author_email='allison@lyonthackston.com',
    license='Apache-2.0',
    python_requires='>=3',
    install_requires=[
        'mkdocs>=1.0.6',
        'click>=7.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'mkdocs.plugins': [
            "simple = mkdocs_simple_plugin.plugin:SimplePlugin"
        ],
        'console_scripts': [
            "mkdocs_simple_gen = mkdocs_simple_plugin.__main__:main"
        ]
    }
)
