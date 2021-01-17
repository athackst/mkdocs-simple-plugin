"""md

## Python Version

You can put _markdown_ in triple-quoted strings in Python.
"""

# md
# ### inline comments
#
# It works in inline comments. The start and end markers must be on their own
# lines.
# /md


def main():
    # noqa: D207
    """<md>Main test.

### docstrings

It works in docstrings. The start and end quotes must be on their own lines.
Drawback: `simple` does not remove leading whitespace.
    """
    print("Hello, world!")
    return 0
