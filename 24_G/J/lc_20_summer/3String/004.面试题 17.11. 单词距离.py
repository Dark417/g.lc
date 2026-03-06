"""
004.面试题 17.11. 单词距离

有个内含单词的超大文本文件，给定任意两个单词，
找出在这个文件中这两个单词的最短距离(相隔单词数)。
如果寻找过程在这个文件中会重复多次，而每次寻找的单词不同，你能对此优化吗?

示例：

输入：words = ["I","am","a","student","from","a","university",
"in","a","city"], word1 = "a", word2 = "student"
输出：1



"""

def findClosest(self, words: List[str], word1: str, word2: str) -> int:
    p1, p2 = [],[]
    for i in range(len(words)):
        if words[i] == word1: p1.append(i)
        if words[i] == word2: p2.append(i)
    i = j = 0
    ans = 100000
    while i < len(p1) and j < len(p2):
        val = abs(p1[i]-p2[j])
        if val == 1: return 1
        if val < ans: ans = val
        if p1[i] < p2[j]: i+=1
        else: j+=1
    return ans

    ans = float("inf")


def findClosest(self, words: List[str], word1: str, word2: str) -> int:
    ind1 = ind2 = -1
    ans = float("inf")
    for i in range(len(words)):
        if words[i] == word1: ind1 = i
        if words[i] == word2: ind2 = i
        if abs(ind1 - ind2) == 1: return 1
        else:
            if ind1 >=0 and ind2 >= 0:
                if abs(ind1 - ind2) < ans: ans = abs(ind1 - ind2)
    return ans

    subRes = []
    for i in range(len(indice1)):
        for j in range(len(indice2)):
            subRes.append(abs(indice1[i] - indice2[j]))
    
    return min(subRes)

def findClosest(self, words, word1, word2):
    word_dict = {}
    for ind, word in enumerate(words):
        if word not in word_dict:
            word_dict[word] = []
        word_dict[word].append(ind)
    p, q = 0, 0
    min_dist = float('inf')
    len_1 = len(word_dict[word1])
    len_2 = len(word_dict[word2])
    while p < len_1 and q < len_2:
        ind_1 = word_dict[word1][p]
        ind_2 = word_dict[word2][q]
        dist = abs(ind_1 - ind_2)
        if dist < min_dist:
            min_dist = dist
        if ind_1 > ind_2:
            q += 1
        else:
            p += 1

    return min_dist


def findClosest(self, words: List[str], word1: str, word2: str) -> int:
    w1_idx = -1
    w2_idx = -1
    dis = 200000
    for i in range(len(words)):
        if words[i] == word1:
            w1_idx = i
        if words[i] == word2:
            w2_idx = i
        if w1_idx>=0 and w2_idx>=0:
            tmp_dis = abs(w1_idx - w2_idx)
            if tmp_dis<dis:
                dis = tmp_dis
    return dis




























