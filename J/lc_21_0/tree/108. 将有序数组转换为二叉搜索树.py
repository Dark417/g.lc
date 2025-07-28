# 108. 将有序数组转换为二叉搜索树

def sortedArrayToBST(self, nums: List[int]) -> TreeNode:
    if not nums:
        return None
    k = len(nums) // 2
    node = TreeNode(nums[k])
    node.left = self.sortedArrayToBST(nums[:k])
    node.right = self.sortedArrayToBST(nums[k+1:])
    return node


def sortedArrayToBST(self, nums: List[int]) -> TreeNode:
    def helper(left, right):
        if left > right:
            return None

        # 总是选择中间位置左边的数字作为根节点
        mid = (left + right) // 2

        root = TreeNode(nums[mid])
        root.left = helper(left, mid - 1)
        root.right = helper(mid + 1, right)
        return root

    return helper(0, len(nums) - 1)




def sortedArrayToBST(self, nums: List[int]) -> TreeNode:
    def helper(left, right):
        if left > right:
            return None

        # 总是选择中间位置右边的数字作为根节点
        mid = (left + right + 1) // 2

        root = TreeNode(nums[mid])
        root.left = helper(left, mid - 1)
        root.right = helper(mid + 1, right)
        return root

    return helper(0, len(nums) - 1)








