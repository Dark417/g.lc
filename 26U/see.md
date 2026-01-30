
<!-- 
record update => auto generate book.md

1 place to link all
1 q => n types
each type index include the question, all link to the question

x.md => x.py
x.md auto complete
instruction to do it

# before question => update index and book.md
    + notes
    + exp



 -->

## 心得

### backtrack
```python
# permutation
# visited
def q():
    res = []
    path = []
    used = [False] * n
    def backtrack():
        if len(path) == n:
            res.append(path[:])
            return
        for i in range(n):
            if used[i]:
                continue
            path.append(...)
            used[i] = True
            backtrack()
            path.pop()
            used[i] = False
    backtrack()
    return res

# combination
# No visited, iterate from i + 1
def q():
    res = []
    path = []
    def backtrack(start: int):
        if len(path) == k:
            res.append(path[:])
            return
        for i in range(start, n):
            path.append(...)
            backtrack(i + 1)
            path.pop()
    backtrack(0)
    return res


# pruning
# NO explicit, loop
# use i + 1 to increment
def dfs(i: int, left: int) -> None:
    if left == 0:
        # 找到一个合法组合
        ans.append(path.copy())
        return

    if i == len(candidates) or left < 0:
        return

    # 不选
    dfs(i + 1, left)

    # 选
    path.append(candidates[i])
    dfs(i, left - candidates[i])
    path.pop()  # 恢复现场

dfs(0, target)
```


### recursion
```python
# return dfs
def q():
    def dfs():
        if base case:
            return somevalue
        # dfs all the way down
        # or process current level
        return somevalue
    return dfs()

# call dfs, return res
def q():
    res = []
    def dfs():
        ...
        return # Not return anything
    dfs()
    return res

# call itself, enter dfs
def q():
    a = q()
    ...

    return somevalue

# dfs
# 1
# go to bottom, bottom / leaf first
# calc res along the way
# update res 
# return cur to parent
res = [] / float('inf') / 0
def dfs(x):
    y = ..
    dfs(y)
    cur = ...
    nonlocal res
    res = max(res, )
    return max(res, up_to_now) #up_to_prev + y
dfs(init)
return res

# 2
# 

```
### iteration

```python
- how many to iterate
    - if multi level, what # current level?
        - len(cur)

```



#### Basic
```python
class Solution:
    def __init__(self):
        self.maxSum = float("-inf")
    def solution():
        self.maxSum

class Solution:
    def solution():
        n
        def dfs():
            nonlocal n

class Solution:
    def help():
        ...
    def solution():
        self.help()
```

```__slots__```


推算要快


### LinkedHashMap


19. Remove Nth Node From End of List of List
    - consider remove head




boundary-length hash map technique





