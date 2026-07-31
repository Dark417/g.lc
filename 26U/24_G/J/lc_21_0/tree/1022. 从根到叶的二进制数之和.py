# 1022. 从根到叶的二进制数之和



def sumRootToLeaf(self, root: TreeNode) -> int:
    def dfs(node, s):
        if node:
            cur = s + str(node.val)
            if not node.left and not node.right:
                self.l.append(cur)
            dfs(node.left, cur)
            dfs(node.right, cur)
    self.l = []
    dfs(root, "")
    return sum(int(int(i, 2)) for i in self.l)


def sumRootToLeaf(self, root: TreeNode) -> int:
    def dfs(node, s):
        cur = s + str(node.val)
        if not node.left and not node.right:
            self.l.append(cur)
        if node.left:
            dfs(node.left, cur)
        if node.right:
            dfs(node.right, cur)
    self.l = []
    dfs(root, "")
    return sum(int(int(i, 2)) for i in self.l)

'''
public int sumRootToLeaf(TreeNode root) {
        return helper(root, 0);
    }
    public int helper(TreeNode root, int sum){
        //空节点，返回0
        if(root == null) return 0;
        //进位更新
        sum = (sum << 1) + root.val;
        //叶子节点直接返回当前和
        if(root.left == null && root.right == null) return sum;
        //递归
        return helper(root.left, sum) + helper(root.right, sum);
    }

'''























