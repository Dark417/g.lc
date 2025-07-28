# 678. 有效的括号字符串




def checkValidString(self, s: str) -> bool:
    # l表示当前左括号最少可能为多少，r表示当前左括号最多可能是多少，他们之间都可以取到
    l = r = 0
    for c in s:
        if c == '(':
            l += 1
            r += 1
        elif c == ')':
            l -= 1
            r -= 1
        else:
            l -= 1
            r += 1
        if l < 0:
            l += 1
        if r < 0:
            return False
    return l == 0




    
def checkValidString(self, s: str) -> bool:
    leftstack = []
    starstack = []
    for i in range(len(s)):
        if s[i] == "(":
            leftstack.append(i)
        elif s[i] == "*":
            starstack.append(i)
        else:
            if leftstack:
                leftstack.pop()
            elif starstack:
                starstack.pop()
            else:
                return False
    while leftstack and starstack:
        leftindex = leftstack.pop()
        starindex = starstack.pop()
        if leftindex > starindex:
            return False
    return len(leftstack) == 0



def checkValidString(self, s: str) -> bool:
    def help(a):
        cnt = 0
        for c in s if a == 1 else reversed(s):
            if c == '(': cnt += a 
            if c == ')': cnt += -a
            if c == '*': cnt += 1
            if cnt < 0:
                return False
        return True
    return help(1) and help(-1)







"""
public boolean checkValidString(String s) {
        int minCount = 0, maxCount = 0;
        int n = s.length();
        for (int i = 0; i < n; i++) {
            char c = s.charAt(i);
            if (c == '(') {
                minCount++;
                maxCount++;
            } else if (c == ')') {
                minCount = Math.max(minCount - 1, 0);
                maxCount--;
                if (maxCount < 0) {
                    return false;
                }
            } else {
                minCount = Math.max(minCount - 1, 0);
                maxCount++;
            }
        }
        return minCount == 0;
    }



"""




































