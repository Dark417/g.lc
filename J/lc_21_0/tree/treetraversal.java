



class Node 
{ 
    int key; 
    Node left, right; 
  
    public Node(int item) 
    { 
        key = item; 
        left = right = null; 
    } 
} 
  
class BinaryTree 
{ 
    // Root of Binary Tree 
    Node root; 
  
    BinaryTree() 
    { 
        root = null; 
    } 
  
    /* Given a binary tree, print its nodes according to the 
      "bottom-up" postorder traversal. */
    void printPostorder(Node node) 
    { 
        if (node == null) 
            return; 
  
        // first recur on left subtree 
        printPostorder(node.left); 
  
        // then recur on right subtree 
        printPostorder(node.right); 
  
        // now deal with the node 
        System.out.print(node.key + " "); 
    } 
  
    /* Given a binary tree, print its nodes in inorder*/
    void printInorder(Node node) 
    { 
        if (node == null) 
            return; 
  
        /* first recur on left child */
        printInorder(node.left); 
  
        /* then print the data of node */
        System.out.print(node.key + " "); 
  
        /* now recur on right child */
        printInorder(node.right); 
    } 
  
    /* Given a binary tree, print its nodes in preorder*/
    void printPreorder(Node node) 
    { 
        if (node == null) 
            return; 
  
        /* first print data of node */
        System.out.print(node.key + " "); 
  
        /* then recur on left sutree */
        printPreorder(node.left); 
  
        /* now recur on right subtree */
        printPreorder(node.right); 
    }




public static void preOrderRecur(TreeNode head) {
    if (head == null) {
        return;
    }
    System.out.print(head.value + " ");
    preOrderRecur(head.left);
    preOrderRecur(head.right);
}


public static void preOrderIteration(TreeNode head) {
	if (head == null) {
		return;
	}
	Stack<TreeNode> stack = new Stack<>();
	stack.push(head);
	while (!stack.isEmpty()) {
		TreeNode node = stack.pop();
		System.out.print(node.value + " ");
		if (node.right != null) {
			stack.push(node.right);
		}
		if (node.left != null) {
			stack.push(node.left);
		}
	}
}



public List<Integer> preorderTraversal(TreeNode root) {
	List<Integer> pre = new LinkedList<Integer>();
	if(root==null) return pre;
	pre.add(root.val);
	pre.addAll(preorderTraversal(root.left));
	pre.addAll(preorderTraversal(root.right));
	return pre;
}


public List<Integer> preorderTraversal(TreeNode root) {
	List<Integer> pre = new LinkedList<Integer>();
	preHelper(root,pre);
	return pre;
}
public void preHelper(TreeNode root, List<Integer> pre) {
	if(root==null) return;
	pre.add(root.val);
	preHelper(root.left,pre);
	preHelper(root.right,pre);
}





public List<Integer> preorderTraversal(TreeNode node) {
	List<Integer> list = new LinkedList<Integer>();
	Stack<TreeNode> rights = new Stack<TreeNode>();
	while(node != null) {
		list.add(node.val);
		if (node.right != null) {
			rights.push(node.right);
		}
		node = node.left;
		if (node == null && !rights.isEmpty()) {
			node = rights.pop();
		}
	}
    return list;
}


public List<Integer> preorderTraversal(TreeNode root) {
    List<Integer> result = new LinkedList<>();
    Deque<TreeNode> stack = new LinkedList<>();
    stack.push(root);
    while (!stack.isEmpty()) {
        TreeNode node = stack.pop();
        if (node != null) {
            result.add(node.val);
            stack.push(node.right);
            stack.push(node.left);
        }
    }
    return result;
}



public List<Integer> preorderTraversal(TreeNode root) {
	List<Integer> result = new LinkedList<>();
	Deque<TreeNode> stack = new LinkedList<>();
	TreeNode node = root;
	while (node != null || !stack.isEmpty()) {
		if (node != null) {
			result.add(node.val);
			stack.push(node.right);
			node = node.left;
		} else {
			node = stack.pop();
		}
	}
	return result;
}



public List<Integer> preorderIt(TreeNode root) {
	List<Integer> pre = new LinkedList<Integer>();
	if(root==null) return pre;
	Stack<TreeNode> tovisit = new Stack<TreeNode>();
	tovisit.push(root);
	while(!tovisit.empty()) {
		TreeNode visiting = tovisit.pop();
		pre.add(visiting.val);
		if(visiting.right!=null) tovisit.push(visiting.right);
		if(visiting.left!=null) tovisit.push(visiting.left);
	}
	return pre;
}




public class Solution {
    public List<Integer> preorderTraversal(TreeNode root) {
        Stack<TreeNode> stack = new Stack<>();
        List<Integer> list = new ArrayList<>();
        TreeNode cur = root;
        while(!stack.isEmpty() || cur != null){
            while(cur != null){
                list.add(cur.val);
                stack.push(cur);
                cur = cur.left;
            }
            cur = stack.pop();
            cur = cur.right;
        }
        return list;
    }
}



public class Solution {
    public List<Integer> preorderTraversal(TreeNode root) {
        List<Integer> res = new ArrayList<>();
        if (root == null)
            return res;
        Stack<TreeNode> s = new Stack<>();
        s.push(root);
        while (!s.isEmpty()) {
            TreeNode cur = s.pop();
            res.add(cur.val);
            if (cur.right != null)
                s.push(cur.right);
            if (cur.left != null)
                s.push(cur.left);
        }
        return res;
    }
}



public class Solution {
    public List<Integer> preorderTraversal(TreeNode root) {
        List<Integer> res = new ArrayList<>();
        if (root == null)
            return res;
        Stack<TreeNode> s = new Stack<>();
        s.push(root);
        while (!s.isEmpty()) {
            TreeNode cur = s.pop();
            while (cur != null) {
                res.add(cur.val);
                s.push(cur.right);
                cur = cur.left;
            }
        }
        return res;
    }
}





public class Solution {
    public List<Integer> preorderTraversal(TreeNode root) {
        Stack<TreeNode> stack = new Stack<>();
        List<Integer> list = new ArrayList<>();
        TreeNode cur = root;
        while(!stack.isEmpty() || cur != null){
            while(cur != null){
                stack.push(cur);
                cur = cur.left;
            }
            cur = stack.pop();
            list.add(cur.val);
            cur = cur.right;
        }
        return list;
    }
}




public static void inOrderRecur(TreeNode head) {
    if (head == null) {
        return;
    }
    preOrderRecur(head.left);
    System.out.print(head.value + " ");
    preOrderRecur(head.right);
}


public static void inOrderIteration(TreeNode head) {
	if (head == null) {
		return;
	}
	TreeNode cur = head;
	Stack<TreeNode> stack = new Stack<>();
	while (!stack.isEmpty() || cur != null) {
		while (cur != null) {
			stack.push(cur);
			cur = cur.left;
		}
		TreeNode node = stack.pop();
		System.out.print(node.value + " ");
		if (node.right != null) {
			cur = node.right;
		}
	}
}









public static void postOrderRecur(TreeNode head) {
    if (head == null) {
        return;
    }
    postOrderRecur(head.left);
    postOrderRecur(head.right);
    System.out.print(head.value + " ");
}


public static void postOrderIteration(TreeNode head) {
		if (head == null) {
			return;
		}
		Stack<TreeNode> stack1 = new Stack<>();
		Stack<TreeNode> stack2 = new Stack<>();
		stack1.push(head);
		while (!stack1.isEmpty()) {
			TreeNode node = stack1.pop();
			stack2.push(node);
			if (node.left != null) {
				stack1.push(node.left);
			}
			if (node.right != null) {
				stack1.push(node.right);
			}
		}
		while (!stack2.isEmpty()) {
			System.out.print(stack2.pop().value + " ");
		}
	}




public static void preOrderMorris(TreeNode head) {
	if (head == null) {
		return;
	}
	TreeNode cur1 = head;//当前开始遍历的节点
	TreeNode cur2 = null;//记录当前结点的左子树
	while (cur1 != null) {
		cur2 = cur1.left;
		if (cur2 != null) {
			while (cur2.right != null && cur2.right != cur1) {//找到当前左子树的最右侧节点，且这个节点应该在指向根结点之前，否则整个节点又回到了根结点。
				cur2 = cur2.right;
			}
			if (cur2.right == null) {//这个时候如果最右侧这个节点的右指针没有指向根结点，创建连接然后往下一个左子树的根结点进行连接操作。
				cur2.right = cur1;
				cur1 = cur1.left;
				continue;
			} else {//当左子树的最右侧节点有指向根结点，此时说明我们已经回到了根结点并重复了之前的操作，同时在回到根结点的时候我们应该已经处理完 左子树的最右侧节点 了，把路断开。
				cur2.right = null;
			}
		} 
		cur1 = cur1.right;//一直往右边走，参考图
	}
}



public static void preOrderMorris(TreeNode head) {
	if (head == null) {
		return;
	}
	TreeNode cur1 = head;
	TreeNode cur2 = null;
	while (cur1 != null) {
		cur2 = cur1.left;
		if (cur2 != null) {
			while (cur2.right != null && cur2.right != cur1) {
				cur2 = cur2.right;
			}
			if (cur2.right == null) {
				cur2.right = cur1;
				System.out.print(cur1.value + " ");
				cur1 = cur1.left;
				continue;
			} else {
				cur2.right = null;
			}
		} else {
			System.out.print(cur1.value + " ");
		}
		cur1 = cur1.right;
	}
}


public static void inOrderMorris(TreeNode head) {
	if (head == null) {
		return;
	}
	TreeNode cur1 = head;
	TreeNode cur2 = null;
	while (cur1 != null) {
		cur2 = cur1.left;
		//构建连接线
		if (cur2 != null) {
			while (cur2.right != null && cur2.right != cur1) {
				cur2 = cur2.right;
			}
			if (cur2.right == null) {
				cur2.right = cur1;
				cur1 = cur1.left;
				continue;
			} else {
				cur2.right = null;
			}
		}
		System.out.print(cur1.value + " ");
		cur1 = cur1.right;
	}
}


//后序Morris
public static void postOrderMorris(TreeNode head) {
	if (head == null) {
		return;
	}
	TreeNode cur1 = head;//遍历树的指针变量
	TreeNode cur2 = null;//当前子树的最右节点
	while (cur1 != null) {
		cur2 = cur1.left;
		if (cur2 != null) {
			while (cur2.right != null && cur2.right != cur1) {
				cur2 = cur2.right;
			}
			if (cur2.right == null) {
				cur2.right = cur1;
				cur1 = cur1.left;
				continue;
			} else {
				cur2.right = null;
				postMorrisPrint(cur1.left);
			}
		}
		cur1 = cur1.right;
	}
	postMorrisPrint(head);
}
//打印函数
public static void postMorrisPrint(TreeNode head) {
	TreeNode reverseList = postMorrisReverseList(head);
	TreeNode cur = reverseList;
	while (cur != null) {
		System.out.print(cur.value + " ");
		cur = cur.right;
	}
	postMorrisReverseList(reverseList);
}
//翻转单链表
public static TreeNode postMorrisReverseList(TreeNode head) {
	TreeNode cur = head;
	TreeNode pre = null;
	while (cur != null) {
		TreeNode next = cur.right;
		cur.right = pre;
		pre = cur;
		cur = next;
	}
	return pre;
}












































