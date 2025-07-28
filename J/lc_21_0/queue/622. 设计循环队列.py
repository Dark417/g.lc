# 622. 设计循环队列


class Node:
    def __init__(self, value, nextNode=None):
        self.value = value
        self.next = nextNode

class MyCircularQueue:

    def __init__(self, k: int):
        """
        Initialize your data structure here. Set the size of the queue to be k.
        """
        self.capacity = k
        self.head = None
        self.tail = None
        self.count = 0

    def enQueue(self, value: int) -> bool:
        """
        Insert an element into the circular queue. Return true if the operation is successful.
        """
        if self.count == self.capacity:
            return False
        
        if self.count == 0:
            self.head = Node(value)
            self.tail = self.head
        else:
            newNode = Node(value)
            self.tail.next = newNode
            self.tail = newNode
        self.count += 1
        return True


    def deQueue(self) -> bool:
        """
        Delete an element from the circular queue. Return true if the operation is successful.
        """
        if self.count == 0:
            return False
        self.head = self.head.next
        self.count -= 1
        return True


    def Front(self) -> int:
        """
        Get the front item from the queue.
        """
        if self.count == 0:
            return -1
        return self.head.value

    def Rear(self) -> int:
        """
        Get the last item from the queue.
        """
        # empty queue
        if self.count == 0:
            return -1
        return self.tail.value
    
    def isEmpty(self) -> bool:
        """
        Checks whether the circular queue is empty or not.
        """
        return self.count == 0

    def isFull(self) -> bool:
        """
        Checks whether the circular queue is full or not.
        """
        return self.count == self.capacity





"""
class Node {
  public int value;
  public Node nextNode;

  public Node(int value) {
    this.value = value;
    this.nextNode = null;
  }
}

    
class MyCircularQueue {

  private Node head, tail;
  private int count;
  private int capacity;

  /** Initialize your data structure here. Set the size of the queue to be k. */
  public MyCircularQueue(int k) {
    this.capacity = k;
  }

  /** Insert an element into the circular queue. Return true if the operation is successful. */
  public boolean enQueue(int value) {
    if (this.count == this.capacity)
      return false;

    Node newNode = new Node(value);
    if (this.count == 0) {
      head = tail = newNode;
    } else {
      tail.nextNode = newNode;
      tail = newNode;
    }
    this.count += 1;
    return true;
  }

  /** Delete an element from the circular queue. Return true if the operation is successful. */
  public boolean deQueue() {
    if (this.count == 0)
      return false;
    this.head = this.head.nextNode;
    this.count -= 1;
    return true;
  }

  /** Get the front item from the queue. */
  public int Front() {
    if (this.count == 0)
      return -1;
    else
      return this.head.value;
  }

  /** Get the last item from the queue. */
  public int Rear() {
    if (this.count == 0)
      return -1;
    else
      return this.tail.value;
  }

  /** Checks whether the circular queue is empty or not. */
  public boolean isEmpty() {
    return (this.count == 0);
  }

  /** Checks whether the circular queue is full or not. */
  public boolean isFull() {
    return (this.count == this.capacity);
  }
}




"""


class MyCircularQueue:

    def __init__(self, k):
        """
        Initialize your data structure here. Set the size of the queue to be k.
        :type k: int
        """
        self.size = k+1
        self.data = [0]*self.size
        self.head = self.rear = 0

    def enQueue(self, value):
        """
        Insert an element into the circular queue. Return true if the operation is successful.
        :type value: int
        :rtype: bool
        """
        if self.isFull():
            return False
        self.data[self.rear] = value
        self.rear = (self.rear+1)%self.size
        return True
    def deQueue(self):
        """
        Delete an element from the circular queue. Return true if the operation is successful.
        :rtype: bool
        """
        if self.isEmpty():
            return False
        self.head = (self.head+1)%self.size
        return True
        
    def Front(self):
        """
        Get the front item from the queue.
        :rtype: int
        """
        if self.isEmpty():
            return -1
        return self.data[self.head]
        

    def Rear(self):
        """
        Get the last item from the queue.
        :rtype: int
        """
        if self.isEmpty():
            return -1
        return self.data[(self.rear-1)%self.size]

    def isEmpty(self):
        """
        Checks whether the circular queue is empty or not.
        :rtype: bool
        """
        return self.head ==self.rear
        

    def isFull(self):
        """
        Checks whether the circular queue is full or not.
        :rtype: bool
        """
        return (self.head - self.rear)%self.size ==1



"""

public class MyCircularQueue {
    private int[] data;
    private int head;
    private int tail;
    private int size;

    // 数组空间大小为k,实际队列大小为k-1，浪费浪一个数组空间
    public MyCircularQueue(int k) { 
        data = new int[k];
        tail = 0;
        head = 0;
        size = k;
    }

    public boolean enQueue(int value) {
        if (isFull()) {   // isFull和isEmpty省略了this
            return false;
        }
        tail = (tail + 1) % size;
        data[tail] = value;
        return true;
    }

    public boolean deQueue() {
        if (isEmpty()) {
            return false;
        }
        head = (head + 1) % size;
        return true;
    }

    public int head() {
        if (isEmpty()) {
            return -1;
        }
        return data[head+1];
    }

    public int tail() {
        if (isEmpty()) {
            return -1;
        }
        return data[tail];
    }

    public boolean isEmpty() {  
        if (head == tail)
            return true;
        return false;
    }

    public boolean isFull() {
        if ((tail + 1) % size == head)   // 尾指针在头指针前面一位则满
            return true;
        return false;
    }
}


class MyCircularQueue {

    private int[] data;
    private int head;
    private int tail;
    private int size;

    /** Initialize your data structure here. Set the size of the queue to be k. */
    public MyCircularQueue(int k) {
        data = new int[k];
        head = -1;
        tail = -1;
        size = k;
    }

    /** Insert an element into the circular queue. Return true if the operation is successful. */
    public boolean enQueue(int value) {
        if (isFull() ) {   // isFull和isEmpty省略了this
            return false;
        }
        if (isEmpty()) {
            head = 0;
        }
        tail = (tail + 1) % size;
        data[tail] = value;
        return true;
    }

    /** Delete an element from the circular queue. Return true if the operation is successful. */
    public boolean deQueue() {
        if (isEmpty()) {
            return false;
        }
        // 头尾指针相同时，证明只剩一个元素，出队后则队列为空，将指针初始化归位
        if (head == tail) {   // 最后一个元素出队head=-1作为isEmpty方法判据
            head = -1;
            tail = -1;
            return true;
        }
        head = (head + 1) % size;  // 出队一个，头指针下移一位，取余时为了在大小k的数组中循环。
        return true;
    }

    /** Get the head item from the queue. */
    public int head() {
        if (isEmpty() ) {
            return -1;
        }
        return data[head];
    }

    /** Get the last item from the queue. */
    public int tail() {
        if (isEmpty()) {
            return -1;
        }
        return data[tail];
    }

    /** Checks whether the circular queue is empty or not. */
    public boolean isEmpty() {
        return head == -1;
    }

    /** Checks whether the circular queue is full or not. */
    public boolean isFull() { // 尾指针在头指针前面一位，证明队列已满
        return ((tail + 1) % size) == head;
    }
}



"""


