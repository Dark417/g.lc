# Trie

## Index

### Easy
- [E] [14. Longest Common Prefix](https://leetcode.cn/problems/longest-common-prefix/)
  `Find the longest string shared as a prefix among all input strings.`
  `String`

### Medium
- [M] [79. 单词搜索](https://leetcode.cn/problems/word-search/)
  `Check whether a word can be formed by navigating adjacent grid cells without reuse.`
  `Backtracking` `Matrix` `DFS`
- [M] [208. 实现 Trie (前缀树)](https://leetcode.cn/problems/implement-trie-prefix-tree/)
  `Implement insert/search/startsWith on a lowercase English Trie.`
  `Trie` `Design` `String`
- [M] [211. 添加与搜索单词 - 数据结构设计](https://leetcode.cn/problems/design-add-and-search-words-data-structure/)
  `Support wildcard searches ('.') over a word dictionary built with a Trie.`
  `Design` `Trie` `DFS`

### Hard
- [H] [212. 单词搜索 II](https://leetcode.cn/problems/word-search-ii/)
  `Find every word from a list that can be traced out on the board without revisiting cells.`
  `Trie` `Backtracking` `DFS`

## Solutions (Python)

<a id="lc-0014"></a>
#### 14. [Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) [E]
`String`
- Compute the longest shared prefix among all strings by shrinking the candidate until every string matches.

##### Approach 1: Iterative prefix shrinking
Use the first word as the candidate prefix and reduce it until every string starts with it.

```python
from typing import List

class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        prefix = strs[0]
        for s in strs[1:]:
            while not s.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix
# Time: O(S), Space: O(1) where S is total characters across all strings
```

##### Approach 2: Zip columns
Traverse columns across all strings simultaneously and break once a column has differing characters.

```python
from typing import List

class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        res = []
        for chars in zip(*strs):
            if len(set(chars)) != 1:
                break
            res.append(chars[0])
        return "".join(res)
# Time: O(S), Space: O(minLen) where minLen is length of shortest string
```

<a id="lc-0079"></a>
#### 79. [单词搜索](https://leetcode.com/problems/word-search/) [M]
`Backtracking` `Matrix` `DFS`
- Perform DFS from each cell, marking visited cells so the same letter is not reused and backtracking upon dead ends.

##### Approach 1: Backtracking DFS
Explore the board recursively, reverting the visited flag when retreating so other paths remain available.

```python
from typing import List

class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        ROWS, COLS = len(board), len(board[0])

        def dfs(r: int, c: int, i: int) -> bool:
            if i == len(word):
                return True
            if not (0 <= r < ROWS and 0 <= c < COLS) or board[r][c] != word[i]:
                return False
            tmp = board[r][c]
            board[r][c] = "#"
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                if dfs(r + dr, c + dc, i + 1):
                    return True
            board[r][c] = tmp
            return False

        for r in range(ROWS):
            for c in range(COLS):
                if dfs(r, c, 0):
                    return True
        return False
# Time: O(MN * 4^L), Space: O(L) where L is word length
```

<a id="lc-0208"></a>
#### 208. [实现 Trie (前缀树)](https://leetcode.com/problems/implement-trie-prefix-tree/) [M]
`Trie` `Design` `String`
- Build a Trie over lowercase letters and support insert/search/startsWith with O(length) time per operation.

##### Approach 1: Array-based Trie
Each node holds an array of 26 children plus an end flag.

```python
class Trie:
    def __init__(self):
        self.children = [None] * 26
        self.isEnd = False

    def _searchNode(self, word: str):
        node = self
        for ch in word:
            idx = ord(ch) - ord("a")
            if not node.children[idx]:
                return None
            node = node.children[idx]
        return node

    def insert(self, word: str) -> None:
        node = self
        for ch in word:
            idx = ord(ch) - ord("a")
            if not node.children[idx]:
                node.children[idx] = Trie()
            node = node.children[idx]
        node.isEnd = True

    def search(self, word: str) -> bool:
        node = self._searchNode(word)
        return bool(node and node.isEnd)

    def startsWith(self, prefix: str) -> bool:
        return self._searchNode(prefix) is not None
# Time: O(L), Space: O(26L) per word
```

<a id="lc-0211"></a>
#### 211. [添加与搜索单词 - 数据结构设计](https://leetcode.com/problems/design-add-and-search-words-data-structure/) [M]
`Design` `Trie` `DFS`
- Extend the Trie with wildcard support by branching over `.` characters during search.

##### Approach 1: Trie with DFS
Use recursion to explore every child whenever the current pattern character is `.`.

```python
class WordDictionary:
    def __init__(self):
        self.children = {}
        self.isWord = False

    def addWord(self, word: str) -> None:
        node = self
        for ch in word:
            if ch not in node.children:
                node.children[ch] = WordDictionary()
            node = node.children[ch]
        node.isWord = True

    def search(self, word: str) -> bool:
        def dfs(index: int, node: "WordDictionary") -> bool:
            if index == len(word):
                return node.isWord
            ch = word[index]
            if ch == ".":
                for child in node.children.values():
                    if dfs(index + 1, child):
                        return True
                return False
            if ch not in node.children:
                return False
            return dfs(index + 1, node.children[ch])

        return dfs(0, self)
# Time: O(26^m * L) worst-case for pattern with `m` dots, Space: O(L)
```

<a id="lc-0212"></a>
#### 212. [单词搜索 II](https://leetcode.com/problems/word-search-ii/) [H]
`Trie` `Backtracking` `DFS`
- Build a Trie from the word list and traverse the board, pruning branches when prefixes disappear.

##### Approach 1: Trie + DFS with pruning
Store full words at trie nodes, DFS removes matches and prunes empty subtrees to avoid revisiting found words.

```python
from typing import List

class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None

class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = TrieNode()
        for word in words:
            node = root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.word = word

        ROWS, COLS = len(board), len(board[0])
        res = []

        def dfs(r: int, c: int, node: TrieNode) -> None:
            ch = board[r][c]
            nxt = node.children.get(ch)
            if not nxt:
                return
            if nxt.word:
                res.append(nxt.word)
                nxt.word = None
            board[r][c] = "#"
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    dfs(nr, nc, nxt)
            board[r][c] = ch
            if not nxt.children:
                node.children.pop(ch)

        for r in range(ROWS):
            for c in range(COLS):
                dfs(r, c, root)
        return res
# Time: O(MN * 4L), Space: O(W * L) where W number of words, L longest word
```

### 386. 字典序排数
`Trie`
```python


```
### 440. 字典序第 K 小的数字
`Trie`
```python
```

### 676. 实现一个魔法字典
```python
class MagicDictionary:

    def __init__(self):
        self.children = {}
        self.isEnd = False

    def buildDict(self, dictionary: List[str]) -> None:
        for word in dictionary:
            cur = self
            for ch in word:
                if ch not in cur.children:
                    cur.children[ch] = MagicDictionary()
                cur = cur.children[ch]
            cur.isEnd = True

    def search(self, searchWord: str) -> bool:
        def dfs(node, pos, modified):
            if pos == len(searchWord):
                return modified and node.isEnd
            ch = searchWord[pos]
            if ch in node.children:
                if dfs(node.children[ch], pos + 1, modified):
                    return True
            if not modified:
                for cnext in node.children:
                    if ch != cnext:
                        if dfs(node.children[cnext], pos + 1, True):
                            return True
            return False
        return dfs(self, 0, False)
```

### 720. 词典中最长的单词
`Trie`
```python
```
