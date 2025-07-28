"""
091.320	Generalized Abbreviation

请你写出一个能够举单词全部缩写的函数。

注意：输出的顺序并不重要。

示例：

输入: "word"
输出:
["word", "1ord", "w1rd", "wo1d", "wor1", "2rd", "w2d", "wo2", "1o1d", "1

来源：力扣（LeetCode）
链接：https://leetcode-cn.com/problems/generalized-abbreviation
著作权归领扣网络所有。商业转载请联系官方授权，非商业转载请注明出处。


"""


def generateAbbreviations(self, word: str) -> List[str]:
    res = []
    
    def helper(i, tmp, cnt):
        """
        cnt 代表前面已经记录多少数字了
        """
        if i == len(word):
            if cnt > 0: tmp += str(cnt)
            res.append(tmp)
        else:
            helper(i + 1, tmp, cnt + 1)
            helper(i + 1, tmp + (str(cnt) if cnt > 0 else "") + word[i], 0)
        
    helper(0, "", 0)
    return res





def generateAbbreviations(self, word: str) -> List[str]:
    res = []
    n = len(word)
    
    def helper(i, tmp):
        if i == n:
            res.append(tmp)
        else:
            for j in range(i, n):
                num = str(j - i) if j - i > 0 else ""
                helper(j + 1, tmp + num + word[j])
            helper(n, tmp + str(n - i))
    
    helper(0, "")
    return res




"""
0 -- 0000 --- word
1 -- 0001 --- wor1
2 -- 0010 --- wo1d
3 -- 0011 --- wo2
4 -- 0100 --- w1rd


"""

def generateAbbreviations(self, word: str) -> List[str]:
    n = len(word)
    res = []
    for i in range(2 ** n):
        tmp = ""
        # 记录1的个数
        one_cnt = 0
        for w, f in zip(word, bin(i)[2:].rjust(n, "0")):
            if f == "0":
                if one_cnt > 0:
                    tmp += str(one_cnt)
                    one_cnt = 0
                tmp += w
            else:
                one_cnt += 1
        if one_cnt > 0:
            tmp += str(one_cnt)
        res.append(tmp)
    return res


def generateAbbreviations(self, word):
    self.res = []
    self.backtrack(word, 0)
    return self.res + [word]
    
    
def backtrack(self, word, index):
    for i in range(index, len(word)):
        for j in range(1, len(word) - i + 1):
            abbrev = word[:i] + str(j) + word[i + j:]
            self.res.append(abbrev)
            self.backtrack(word[:i] + str(j) + word[i + j:], i + len(str(j)) + 1)



def generateAbbreviations(self, word: str) -> List[str]:
    ans = []
    def backtrace(cur='', i=0):
        if i == len(word):
            ans.append(cur)
            return
        
        backtrace(cur + word[i], i+1)
        if not (cur and cur[-1].isdigit()):
            for j in range(i, len(word)):
                backtrace(cur+str(j-i+1), j+1)
    backtrace()
    return ans



def generateAbbreviations(self, word: str) -> List[str]:
    if len(word) == 0:
        return [""]
    s = word[0]
    ans = []
    for w in self.generateAbbreviations(word[1:]):
        j = 0
        while j < len(w) and w[j].isdigit():
            j += 1 
        if j == 0:
            ans.append(s+w) #不缩写
            ans.append("1"+w) #缩写
        else:
            ans.append(s+w) #不缩写
            ans.append(str(int(w[:j])+1)+w[j:]) #缩写
    return ans































