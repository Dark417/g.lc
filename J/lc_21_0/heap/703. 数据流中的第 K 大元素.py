# 703. 数据流中的第 K 大元素

def __init__(self, k, nums):
    self.k = k
    self.heap = nums
    heapq.heapify(self.heap)
    while len(self.heap) > k:
        heapq.heappop(self.heap)

def add(self, val):
	if len(self.heap) < self.k:
        heapq.heappush(self.heap, val)
    elif self.heap[0] < val:
        heapq.heapreplace(self.heap, val)

    return self.heap[0]



"""
public class KthLargest {

    private PriorityQueue<Integer> queue;
    private int limit;

    public KthLargest(int k, int[] nums) {
        limit = k;
        queue = new PriorityQueue<>(k);
        for (int num : nums) {
            add(num);
        }
    }

    public int add(int val) {
        if (queue.size() < limit) {
            queue.add(val);
        } else if (val > queue.peek()) {
            queue.poll();
            queue.add(val);
        }

        return queue.peek();
    }

}




"""











































