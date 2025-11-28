def buggy(n):
    if n==0:
        return 0
    return buggy(n - 1)

print(buggy(3))