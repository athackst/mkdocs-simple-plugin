This paragraph is here to make sure the extraction starts immediately.
# Coffee Fibonacci

Although trite, this is an example of the sum recurrence.

    fib = (n) ->
      # Base cases
      if n in [ 1 , 2 ]
        return 1
      # Recursive calls
      fib(n-1) + fib(n-2)

## Example usage
This is perfectly good Markdown commentary, but will not appear in the
extracted doc page.

    fib(3) # => fib(2) + fib(1) => 2

    # DOCPAGE
## Complexity
This note about complexity will appear in the doc page.
