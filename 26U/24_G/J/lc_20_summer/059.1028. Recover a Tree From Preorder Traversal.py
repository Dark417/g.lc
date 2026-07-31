"""
059.1028. Recover a Tree From Preorder Traversal
从先序遍历还原二叉树

We run a preorder depth first search on the root of a binary tree.

At each node in this traversal, we output D dashes (where D is the depth of this 
node), then we output the value of this node.  (If the depth of a node is D, 
the depth of its immediate child is D+1.  The depth of the root node is 0.)

If a node has only one child, that child is guaranteed to be the left child.

Given the output S of this traversal, recover the tree and return its root.

 

Example 1:



Input: "1-2--3--4-5--6--7"
Output: [1,2,5,3,4,6,7]
Example 2:



Input: "1-2--3---4-5--6---7"
Output: [1,2,5,3,null,6,null,4,null,7]
 

Example 3:



Input: "1-401--349---90--88"
Output: [1,401,null,349,88,90]
 

Note:

The number of nodes in the original tree is between 1 and 1000.
Each node will have a value between 1 and 10^9.

"""

def recoverFromPreorder(self, S):
    stack, i = [], 0
    while i < len(S):
        level, val = 0, ""
        while i < len(S) and S[i] == '-':
            level, i = level + 1, i + 1
        while i < len(S) and S[i] != '-':
            val, i = val + S[i], i + 1
        while len(stack) > level:
            stack.pop()
        node = TreeNode(val)
        if stack and stack[-1].left is None:
            stack[-1].left = node
        elif stack:
            stack[-1].right = node
        stack.append(node)
    return stack[0]


def recoverFromPreorder(self, S):
    vals = [(len(s[1]), int(s[2])) for s in re.findall("((-*)(\d+))", S)][::-1]

    def fn(level):
        if not vals or level != vals[-1][0]: return None
        node = TreeNode(vals.pop()[1])
        node.left = fn(level+1)
        node.right = fn(level+1)
        return node
    return fn(0)


public TreeNode recoverFromPreorder(String S) {
    int level, val;
    Stack<TreeNode> stack = new Stack<>();
    for (int i = 0; i < S.length();) {
        for (level = 0; S.charAt(i) == '-'; i++) {
            level++;
        }
        for (val = 0; i < S.length() && S.charAt(i) != '-'; i++) {
            val = val * 10 + (S.charAt(i) - '0');
        }
        while (stack.size() > level) {
            stack.pop();
        }
        TreeNode node = new TreeNode(val);
        if (!stack.isEmpty()) {
            if (stack.peek().left == null) {
                stack.peek().left = node;
            } else {
                stack.peek().right = node;
            }
        }
        stack.add(node);
    }
    while (stack.size() > 1) {
        stack.pop();
    }
    return stack.pop();
}


TreeNode* recoverFromPreorder(string S) {
    vector<TreeNode*> stack;
    for (int i = 0, level, val; i < S.length();) {
        for (level = 0; S[i] == '-'; i++)
            level++;
        for (val = 0; i < S.length() && S[i] != '-'; i++)
            val = val * 10 + S[i] - '0';
        TreeNode* node = new TreeNode(val);
        while (stack.size() > level) stack.pop_back();
        if (!stack.empty())
            if (!stack.back()->left) stack.back()->left = node;
            else stack.back()->right = node;
        stack.push_back(node);
    }
    return stack[0];
}


#
def recoverFromPreorder(self, S: str) -> TreeNode:
    depth = 0
    dd = collections.defaultdict(TreeNode)
    head = TreeNode(-1)
    dd[-1] = head
    cur_num = ''        
    for i, c in enumerate(S):
        if c != '-':
            if (i < len(S)-1 and S[i+1] != '-'): 
                cur_num += c
            else:
                prev = dd[depth-1]
                cur = TreeNode(cur_num + c)
                dd[depth] = cur
                
                if prev.left:
                    prev.right = cur
                else:
                    prev.left = cur

                depth = 0
                cur_num = ''
        else:
            depth += 1
        
    return head.left


def recoverFromPreorder(self, S: str) -> TreeNode:
    num, depth = 0, 0
    S, depth_map = S + '-', {-1: TreeNode(-1)}
    for i, c in enumerate(S):
        if c == '-':
            depth += 1
        else:
            num = 10 * num + int(S[i])
            if S[i+1] == '-':
                parent = depth_map[depth-1]
                current = depth_map[depth] = TreeNode(num)
                if parent.left:
                    parent.right = current
                else:
                    parent.left = current
                num, depth = 0, 0
    return depth_map[0]


def recoverFromPreorder(self, s: str) -> TreeNode:
    self.index = 0
    def dfs(depth):
        if self.index == len(s):
            return
        for i in range(depth):
            if s[self.index+i] != '-':
                return
        self.index += depth
        curr = 0
        while self.index < len(s) and s[self.index].isdigit():
            curr = curr * 10 + int(s[self.index])
            self.index += 1
        node = TreeNode(curr)
        node.left = dfs(depth+1)
        node.right = dfs(depth+1)
        return node
    return dfs(0)


def recoverFromPreorder(self, S):
    vals = [(len(s[1]), int(s[2])) for s in re.findall("((-*)(\d+))", S)][::-1]

    def fn(level):
        if not vals or level != vals[-1][0]: return None
        node = TreeNode(vals.pop()[1])
        node.left = fn(level+1)
        node.right = fn(level+1)
        return node
    return fn(0)

























































