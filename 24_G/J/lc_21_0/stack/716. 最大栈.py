# 716. 最大栈

class MaxStack(list):
    def push(self, x):
        m = max(x, self[-1][1] if self else None)
        self.append((x, m))

    def pop(self):
        return list.pop(self)[0]

    def top(self):
        return self[-1][0]

    def peekMax(self):
        return self[-1][1]

    def popMax(self):
        m = self[-1][1]
        b = []
        while self[-1][0] != m:
            b.append(self.pop())

        self.pop()
        map(self.push, reversed(b))
        return m


class MaxStack:

    def __init__(self):
        self.num_stk = []
        self.max_stk = []

    def push(self, x: int) -> None:
        if self.max_stk == [] or x > self.max_stk[-1]:
            self.max_stk.append(x)
        else:
            self.max_stk.append(self.max_stk[-1])
        
        self.num_stk.append(x)

    def pop(self) -> int:
        self.max_stk.pop(-1)
        return self.num_stk.pop(-1)

    def top(self) -> int:
        return self.num_stk[-1]

    def peekMax(self) -> int:
        return self.max_stk[-1]

    def popMax(self) -> int:
        cur_max = self.max_stk[-1]

        tmp = []
        while self.num_stk[-1] != cur_max:
            tmp.append(self.pop())          #2个栈一起弹

        self.pop()
        
        while tmp:
            self.push(tmp.pop(-1))          #2个栈一起压
        return cur_max



"""
class MaxStack {
    TreeMap<Integer, List<Node>> map;
    DoubleLinkedList dll;

    public MaxStack() {
        map = new TreeMap();
        dll = new DoubleLinkedList();
    }

    public void push(int x) {
        Node node = dll.add(x);
        if(!map.containsKey(x))
            map.put(x, new ArrayList<Node>());
        map.get(x).add(node);
    }

    public int pop() {
        int val = dll.pop();
        List<Node> L = map.get(val);
        L.remove(L.size() - 1);
        if (L.isEmpty()) map.remove(val);
        return val;
    }

    public int top() {
        return dll.peek();
    }

    public int peekMax() {
        return map.lastKey();
    }

    public int popMax() {
        int max = peekMax();
        List<Node> L = map.get(max);
        Node node = L.remove(L.size() - 1);
        dll.unlink(node);
        if (L.isEmpty()) map.remove(max);
        return max;
    }
}

class DoubleLinkedList {
    Node head, tail;

    public DoubleLinkedList() {
        head = new Node(0);
        tail = new Node(0);
        head.next = tail;
        tail.prev = head;
    }

    public Node add(int val) {
        Node x = new Node(val);
        x.next = tail;
        x.prev = tail.prev;
        tail.prev = tail.prev.next = x;
        return x;
    }

    public int pop() {
        return unlink(tail.prev).val;
    }

    public int peek() {
        return tail.prev.val;
    }

    public Node unlink(Node node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
        return node;
    }
}

class Node {
    int val;
    Node prev, next;
    public Node(int v) {val = v;}
}

"""












