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
    """<md trim=4 >Main test.

    ### docstrings

    It works in docstrings. The start and end quotes must be on their own lines.
    You can even tell it to remove leading whitespace with the 'trim' option.
    """
    print("Hello, world!")
    return 0
