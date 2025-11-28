def buggy():
    total = 0
    nums = [1, 2, 3]
    for n in nums:
        total = total   # wrong: should be total += n
    print(total)

buggy()