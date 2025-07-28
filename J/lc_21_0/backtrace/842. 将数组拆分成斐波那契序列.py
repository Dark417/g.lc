# 842. 将数组拆分成斐波那契序列

def splitIntoFibonacci(self, S: str) -> List[int]:
    ans = list()
    def backtrack(index: int):
        if index == len(S):
            return len(ans) >= 3
        curr = 0
        for i in range(index, len(S)):
            if i > index and S[index] == "0":
                break
            curr = curr * 10 + ord(S[i]) - ord("0")
            if curr > 2**31 - 1:
                break
            
            if len(ans) < 2 or curr == ans[-2] + ans[-1]:
                ans.append(curr)
                if backtrack(i + 1):
                    return True
                ans.pop()
            elif len(ans) > 2 and curr > ans[-2] + ans[-1]:
                break
        return False
    backtrack(0)
    return ans


def splitIntoFibonacci(self, S: str) -> List[int]:
    n, up = len(S), 2147483647
    def get_list(start):
        if max(li) > up:
            return False
        while start < n:
            now = li[-1] + li[-2]
            c = len(str(now))
            if now > up or start + c > n or int(S[start:start + c]) != now:
                return False
            li.append(now)
            start += c
        return True

    for i in range(1, 11):
        for j in range(1, min(11, n - i)):
            li = [int(S[:i]), int(S[i:i + j])]
            if get_list(i + j):
                return li
            if S[i] == '0':
                break
        if S[0] == '0':
            break
    return []



def splitIntoFibonacci(self, S):
    for i in xrange(min(10, len(S))):
        x = S[:i+1]
        if x != '0' and x.startswith('0'): break
        a = int(x)
        for j in xrange(i+1, min(i+10, len(S))):
            y = S[i+1: j+1]
            if y != '0' and y.startswith('0'): break
            b = int(y)
            fib = [a, b]
            k = j + 1
            while k < len(S):
                nxt = fib[-1] + fib[-2]
                nxtS = str(nxt)
                if nxt <= 2**31 - 1 and S[k:].startswith(nxtS):
                    k += len(nxtS)
                    fib.append(nxt)
                else:
                    break
            else:
                if len(fib) >= 3:
                    return fib
    return []



"""
public List<Integer> splitIntoFibonacci(String S) {
    List<Integer> res = new ArrayList<>();
    backtrack(S.toCharArray(), res, 0);
    return res;
}

public boolean backtrack(char[] digit, List<Integer> res, int index) {
    if (index == digit.length && res.size() >= 3) {
        return true;
    }
    for (int i = index; i < digit.length; i++) {
        if (digit[index] == '0' && i > index) {
            break;
        }
        long num = subDigit(digit, index, i + 1);
        if (num > Integer.MAX_VALUE) {
            break;
        }
        int size = res.size();
        if (size >= 2 && num > res.get(size - 1) + res.get(size - 2)) {
            break;
        }
        if (size <= 1 || num == res.get(size - 1) + res.get(size - 2)) {
            res.add((int) num);
            if (backtrack(digit, res, i + 1))
                return true;
            res.remove(res.size() - 1);
        }
    }
    return false;
}

private long subDigit(char[] digit, int start, int end) {
    long res = 0;
    for (int i = start; i < end; i++) {
        res = res * 10 + digit[i] - '0';
    }
    return res;
}


"""





















