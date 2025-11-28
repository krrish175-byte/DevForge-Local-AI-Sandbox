class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def preorder(root, res):
    if not root:
        return
    
    preorder(root.left, res)
    res.append(root.val)
    preorder(root.right, res)

root = Node(1)
root.left = Node(2)
root.right = Node(3)

res = []
preorder(root, res)
print(res)
