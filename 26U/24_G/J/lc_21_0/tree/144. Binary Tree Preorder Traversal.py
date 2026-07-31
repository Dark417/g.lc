'''
144. Binary Tree Preorder Traversal
二叉树的前序遍历


Given the root of a binary tree, return the preorder traversal of its nodes' values.


'''

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


def printPreorder(root):
    if root:
        print(root.val),
        printPreorder(root.left)
        printPreorder(root.right)


def printInorder(root):
    if root:
        printInorder(root.left)
        print(root.val),
        printInorder(root.right)


def printPostorder(root):
    if root:
        printPostorder(root.left)
        printPostorder(root.right)
        print(root.val)


# recursive
def preorderTraversal(self, root: TreeNode) -> List[int]:

    def preorder(node, ret):
        if node:
            ret.append(node.val)
            # if node.left:
            preorder(node.left, ret)
            # if node.right:
            preorder(node.right, ret)

    def inorder(node, ret):
        if node:
            inorder(node.left, ret)
            ret.append(node.val)
            inorder(node.right, ret)

    def postorder(node, ret):
        if node:
            postorder(node.left, ret)
            postorder(node.right, ret)
            ret.append(node.val)

    ret = []
    stackin(root, ret)

    return ret



def preorderTraversal(self, root):
    if not root: return []
    out = []
    out.append(root.val)
    out.extend(self.preorderTraversal(root.left))
    out.extend(self.preorderTraversal(root.right))
    return out



def preorderTraversal(self, root):
	if not root:
        return []
    else:
        return [root.val] + self.preorderTraversal(root.left) + self.preorderTraversal(root.right)



def preorderTraversal(self, root):
    stack, res = [root], []
    while stack:
        node = stack.pop()
        if node:
            res.append(node.val)
            stack.append(node.right)
            stack.append(node.left)
    return res


# def preorderTraversal(self, root: TreeNode) -> List[int]:
# 	stack, res = [root], []
# 	while stack:
# 		node = stack.pop()
# 		if node:
# 			res.append(node.val)
# 			if node.right:
# 				stack.append(node.right)
# 			if node.left:
# 				stack.append(node.left)
# 		return res



# iterative
def preorderTraversal(self, root: TreeNode) -> List[int]:
	if not root: return []
	cur, stack, res, = root, [], []
	while cur or stack:
		while cur:
			res.append(cur.val)
			stack.append(cur)
			cur = cur.left
		cur = stack.pop()
		cur = cur.right
	return res




def preorderTraversal(self, root: TreeNode) -> List[int]:
    result, stack = [], [(root, False)]

    while stack:
        cur, visited = stack.pop()
        if cur:
            if visited:
                result.append(cur.val)
            else:
                stack.append((cur.right, False))
                stack.append((cur.left, False))
                stack.append((cur, True))

    return result



def preorderTraversal(self, root):
    if root is None: 
        return []
    t = type(root)			                        # 保存树的类型
    out = []				                        # 初始化输出数组
    stack = [root]			                        # 将树压入栈中
    while stack:			                        # 循环栈
        root = stack.pop()	                                # 根节点等于出栈的节点
        if type(root) != t and root is not None:	        # 如果此时root不为树并且不为空
            out.append(root)				        # 将这个数加入输出数组中
            continue						# 结束本次循环
        if root:      						# 如果此时root是树
            stack.append(root.right)				# 将右孩子压入栈
            stack.append(root.left)				# 将左孩子压入栈
            stack.append(root.val)				# 将根的值压入栈
    return out







def preorderTraversal(self, root: TreeNode) -> List[int]:
    res = list()
    if not root:
        return res
    
    p1 = root
    while p1:
        p2 = p1.left
        if p2:
            while p2.right and p2.right != p1:
                p2 = p2.right
            if not p2.right:
                res.append(p1.val)
                p2.right = p1
                p1 = p1.left
                continue
            else:
                p2.right = None
        else:
            res.append(p1.val)
        p1 = p1.right
    
    return res






def MorrisTraversal(root): 
    curr = root 
  
    while curr: 
        # If left child is null, print the 
        # current node data. And, update  
        # the current pointer to right child. 
        if curr.left is None: 
            print(curr.data) 
            curr = curr.right 
  
        else: 
            # Find the inorder predecessor 
            prev = curr.left 
  
            while prev.right is not None and prev.right is not curr: 
                prev = prev.right 
  
            # If the right child of inorder 
            # predecessor already points to 
            # the current node, update the  
            # current with it's right child 
            if prev.right is curr: 
                prev.right = None
                curr = curr.right 
                  
            # else If right child doesn't point 
            # to the current node, then print this 
            # node's data and update the right child 
            # pointer with the current node and update 
            # the current with it's left child 
            else: 
                print(curr.data) 
                prev.right = curr  
                curr = curr.left 










'''
class Solution {
    public List<Integer> preorderTraversal(TreeNode root) {
        List<Integer> res = new ArrayList<Integer>();
        preorder(root, res);
        return res;
    }

    public void preorder(TreeNode root, List<Integer> res) {
        if (root == null) {
            return;
        }
        res.add(root.val);
        preorder(root.left, res);
        preorder(root.right, res);
    }
}


class Solution {
    public List<Integer> preorderTraversal(TreeNode root) {
        List<Integer> res = new ArrayList<Integer>();
        if (root == null) {
            return res;
        }

        Deque<TreeNode> stack = new LinkedList<TreeNode>();
        TreeNode node = root;
        while (!stack.isEmpty() || node != null) {
            while (node != null) {
                res.add(node.val);
                stack.push(node);
                node = node.left;
            }
            node = stack.pop();
            node = node.right;
        }
        return res;
    }
}

'''
