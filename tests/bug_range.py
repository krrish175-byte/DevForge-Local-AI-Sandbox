def buggy():
    arr = [5, 10, 15]
    for i in range(-1, 3):  # runtime bug: starts at -1
        print(arr[i])

buggy()