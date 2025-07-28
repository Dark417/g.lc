# 653. 两数之和 IV - 输入 BST


def findTarget(self, root: TreeNode, k: int) -> bool:
    def dfs(node):
        if not node:
            return False
        if node.val in self.s:
            return True
        self.s.add(k - node.val)
        return dfs(node.left) or dfs(node.right)
    self.s = set()
    return dfs(root)





"""
public class Solution {
    public boolean findTarget(TreeNode root, int k) {
        List < Integer > list = new ArrayList();
        inorder(root, list);
        int l = 0, r = list.size() - 1;
        while (l < r) {
            int sum = list.get(l) + list.get(r);
            if (sum == k)
                return true;
            if (sum < k)
                l++;
            else
                r--;
        }
        return false;
    }
    public void inorder(TreeNode root, List < Integer > list) {
        if (root == null)
            return;
        inorder(root.left, list);
        list.add(root.val);
        inorder(root.right, list);
    }
}


"""


def twoSumBSTs(self, root1: TreeNode, root2: TreeNode, target: int) -> bool:
    def inorder(node):
        if node:
            inorder(node.left)
            self.l.add(node.val)
            inorder(node.right)
    self.l = set()
    inorder(root1)
    
    def dfs(node):
        if not node:
            return False
        if target - node.val in self.l:
            return True
        return dfs(node.left) or dfs(node.right)
    
    return dfs(root2)


    an, bn = len(a), len(b)

    i = 0
    j = bn -1 
    while i < an and 0 <= j:
        if a[i] + b[j] == target:
            return True
        elif a[i] + b[j] < target:
            i += 1
        else:
            j -= 1  
    return False



























