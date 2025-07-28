# 524. 通过删除字母匹配到字典里最长单词

def findLongestWord(self, s: str, d: List[str]) -> str:
    d.sort(key=lambda x: (-len(x), x))#对字典d进行排序，第一关键字是长度降序，第二关键字是字符串本身字典序
    def f(c):                   #匹配函数
        i = 0
        for j in c:             #遍历单词里的字母
            k = s.find(j, i)    #查找函数，后一个参数是查找起点
            if k == -1:
                return False    #查找失败就返回错误
            i = k + 1           #查找成功就更新查找起点
        return True
    for c in d:                 #遍历字符串列表
        if f(c):                #如果符合验证就输出
            return c
    return ''                   #否则输出空串


def findLongestWord(self, s: str, d: List[str]) -> str:
    d.sort(key=lambda x: (-len(x), x))
    def f(c):
        i = 0
        for j in c:
            if (i := s.find(j, i)) == -1:
                return True
            i += 1
    return next((c for c in d if not f(c)), '')


def f(c):
    i = 0
    for j in s:
        if i < len(c) and c[i] == j:
            i += 1
    return i == len(c)
            

def findLongestWord(self, s: str, d: List[str]) -> str:
    def f(c):
        i = 0
        for j in c:
            if (i := s.find(j, i)) == -1:
                return False
            i += 1
        return True
    return next(filter(f, sorted(d, key=lambda x: (-len(x), x))), '')







def findLongestWord(self, s: str, d: List[str]) -> str:
    d.sort(key = lambda x: (-len(x), x))
    for word in d:
        index = 0
        for ch in word:
            index = s.find(ch, index) + 1  # find输出-1:False
            if not index:
                break
        else:       # 这里用else语句保证break之后不会执行，正常循环结束会执行
            return word
    return ''


def findLongestWord(self, s: str, d: List[str]) -> str:
    ans, ans_len = '', 0
    for dStr in d:
        i = j =0
        while i < len(s) and j < len(dStr):
            if s[i] == dStr[j]:
                i += 1
                j += 1
            else:
                i += 1
        if  j == len(dStr):
            if j > ans_len:
                ans, ans_len = dStr, j
            elif j == ans_len and dStr < ans:
                ans = dStr
                ans, ans_len = dStr, j
    return ans


"""
official
https://leetcode-cn.com/problems/longest-word-in-dictionary-through-deleting/solution/tong-guo-shan-chu-zi-mu-pi-pei-dao-zi-dian-li-zui-/

brute force
public String findLongestWord(String s, List < String > d) {
        HashSet < String > set = new HashSet < > (d);
        List < String > l = new ArrayList < > ();
        generate(s, "", 0, l);
        String max_str = "";
        for (String str: l) {
            if (set.contains(str))
                if (str.length() > max_str.length() || (str.length() == max_str.length() && str.compareTo(max_str) < 0))
                    max_str = str;
        }
        return max_str;
    }
    public void generate(String s, String str, int i, List < String > l) {
        if (i == s.length())
            l.add(str);
        else {
            generate(s, str + s.charAt(i), i + 1, l);
            generate(s, str, i + 1, l);
        }
    }




 public boolean isSubsequence(String x, String y) {
    int j = 0;
    for (int i = 0; i < y.length() && j < x.length(); i++)
        if (x.charAt(j) == y.charAt(i))
            j++;
    return j == x.length();
}
public String findLongestWord(String s, List < String > d) {
    Collections.sort(d, new Comparator < String > () {
        public int compare(String s1, String s2) {
            return s2.length() != s1.length() ? s2.length() - s1.length() : s1.compareTo(s2);
        }
    });
    for (String str: d) {
        if (isSubsequence(str, s))
            return str;
    }
    return "";
}




public boolean isSubsequence(String x, String y) {
    int j = 0;
    for (int i = 0; i < y.length() && j < x.length(); i++)
        if (x.charAt(j) == y.charAt(i))
            j++;
    return j == x.length();
}
public String findLongestWord(String s, List < String > d) {
    String max_str = "";
    for (String str: d) {
        if (isSubsequence(str, s)) {
            if (str.length() > max_str.length() || (str.length() == max_str.length() && str.compareTo(max_str) < 0))
                max_str = str;
        }
    }
    return max_str;
}



"""




























