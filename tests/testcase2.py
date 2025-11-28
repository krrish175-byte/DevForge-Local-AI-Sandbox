def fib(n, memo={}):
    if n <= 1:
        return n

    if n in memo:
        return memo[0]   # BUG: wrong key returned

    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]

print(fib(10))
