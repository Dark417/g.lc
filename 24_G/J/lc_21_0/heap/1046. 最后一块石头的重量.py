# 1046. 最后一块石头的重量

def lastStoneWeight(self, stones: List[int]) -> int:
    s = [-i for i in stones]
    heapq.heapify(s)
    
    while len(s) >= 2:
        x1 = heapq.heappop(s)
        x2 = heapq.heappop(s)
        if x1 != x2:
            heapq.heappush(s, x1 - x2)
    return -s[0] if s else 0



class Heap:
    def __init__(self,desc=False):
        self.heap = []
        self.desc = desc
    
    @property
    def size(self):
        return len(self.heap)
    
    def top(self):
        if self.size:
            return self.heap[0]
        return None
    
    def push(self,item):
        self.heap.append(item)
        self._sift_up(self.size-1)
    
    def pop(self):
        item = self.heap[0]
        self._swap(0,self.size-1)
        self.heap.pop()
        self._sift_down(0)
        return item
    
    def _smaller(self,lhs,rhs):
        return lhs > rhs if self.desc else lhs < rhs
    
    def _sift_up(self,index):
        while index:
            parent = (index-1) // 2
            
            if self._smaller(self.heap[parent],self.heap[index]):
                break
                
            self._swap(parent,index)
            index = parent
    
    def _sift_down(self,index):
        while index*2+1 < self.size:
            smallest = index
            left = index*2+1
            right = index*2+2
            
            if self._smaller(self.heap[left],self.heap[smallest]):
                smallest = left
                
            if right < self.size and self._smaller(self.heap[right],self.heap[smallest]):
                smallest = right
                
            if smallest == index:
                break
            
            self._swap(index,smallest)
            index = smallest
    
    def _swap(self,i,j):
        self.heap[i],self.heap[j] = self.heap[j],self.heap[i]

class Solution:
    def lastStoneWeight(self, stones: List[int]) -> int:
        heap = Heap(desc=True)
        for stone in stones:
            heap.push(stone)

        while heap.size > 1:
            x,y = heap.pop(),heap.pop()
            if x != y:
                heap.push(x-y)
        if heap.size: return heap.heap[0]
        return 0
























