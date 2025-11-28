def buggy():
    arr = [1, 2, 3]
    for i in range(len(arr) + 1):
        print(arr[i])

buggy()