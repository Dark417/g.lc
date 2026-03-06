# 989. 数组形式的整数加法


def addToArrayForm(self, A, K):
    A[-1] += K
    for i in xrange(len(A) - 1, -1, -1):
        carry, A[i] = divmod(A[i], 10)
        if i: A[i-1] += carry
    if carry:
        A = map(int, str(carry)) + A
    return A


def addToArrayForm(self, A, K):
    for i in range(len(A) - 1, -1, -1):
        K, A[i] = divmod(A[i] + K, 10)
    return [int(i) for i in str(K)] + A if K else A


def addToArrayForm(self, A: List[int], K: int) -> List[int]:
    i = len(A) - 1
    while K:
        A[i] += K
        K, A[i] = A[i] // 10, A[i] % 10
        i -= 1

        if i < 0 and K:
            A.insert(0,0)
            i = 0
    return A


def addToArrayForm(self, A: List[int], K: int) -> List[int]:
    return list(str(int("".join(map(str, A))) + K))


def addToArrayForm(self, A: List[int], K: int) -> List[int]:
    pdt = 0
    for i in range(len(A)):
        pdt = pdt*10 + A[i]
    
    return list(str(pdt + K))







"""
public List<Integer> addToArrayForm(int[] A, int K) {
    List<Integer> res = new ArrayList<Integer>();
    int n = A.length;
    for (int i = n - 1; i >= 0; --i) {
        int sum = A[i] + K % 10;
        K /= 10;
        if (sum >= 10) {
            K++;
            sum -= 10;
        }
        res.add(sum);
    }
    for (; K > 0; K /= 10) {
        res.add(K % 10);
    }
    Collections.reverse(res);
    return res;
}



public List<Integer> addToArrayForm(int[] A, int K) {
    List<Integer> res = new ArrayList<Integer>();
    int n = A.length;
    for (int i = n - 1; i >= 0 || K > 0; --i, K /= 10) {
        if (i >= 0) {
            K += A[i];
        }
        res.add(K % 10);
    }
    Collections.reverse(res);
    return res;
}


"""



def addToArrayForm(self, A: List[int], K: int) -> List[int]:
    K = list(map(int,str(K)))
    
    res = []
    i,j = len(A)-1,len(K)-1
    carry = 0

    while i >= 0 and j >= 0:
        res.append(A[i] + K[j] + carry)
        res[-1],carry = res[-1] % 10, res[-1] // 10
        i -= 1
        j -= 1
    while i >= 0:
        res.append(A[i] + carry)
        res[-1],carry = res[-1] % 10, res[-1] // 10
        i -= 1
    while j >= 0:
        res.append(K[j] + carry)
        res[-1],carry = res[-1] % 10, res[-1] // 10
        j -= 1

    if carry:
        res.append(1)

    return res[::-1]



