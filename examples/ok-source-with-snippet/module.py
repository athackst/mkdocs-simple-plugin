"""md

## Main file

You can even make snippets to be included as separate files.

This is included using `pymdownx.snippets`
--8<-- "snippet.md"

This is included using `markdown_include.include`
{!snippet.md!}
"""

# md file=snippet.md
#
# ## Snippet
#
# This is a snippet from module.py.
# /md


def main():
    """Main function which prints "Hello, World!"""
    print("Hello, world!")
    return 0
