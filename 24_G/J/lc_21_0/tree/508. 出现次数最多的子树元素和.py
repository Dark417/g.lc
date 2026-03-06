# 508. 出现次数最多的子树元素和


def findFrequentTreeSum(self, root: TreeNode) -> List[int]:
    # 思路，dfs计算所有子树元素和，并用hash表存储各子树元素和出现次数
    def dfs(root):
        """自底向上地（后序遍历），记录所有子树元素和及其出现次数"""
        # 以root为根节点的树的元素和，等于，root.val+左子树元素和+右子树元素和
        if not root:
            return 0
        left = dfs(root.left)
        right = dfs(root.right)
        total = root.val + left + right
        hashmap[total] = hashmap.get(total, 0) + 1
        return total
    
    hashmap = {}
    dfs(root)
    # 对各子树元素和，按出现次数从大到小排序
    sorted_hash = sorted(hashmap.items(), key=lambda x:x[1], reverse=True)
    # 取前面所有次数最多且相同的子树元素和
    res = [sorted_hash[i][0] for i in range(len(sorted_hash)) if sorted_hash[i][1]==sorted_hash[0][1]]
    return res

