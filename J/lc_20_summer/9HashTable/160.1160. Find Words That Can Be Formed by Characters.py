"""
160.1160. Find Words That Can Be Formed by Characters
拼写单词


You are given an array of strings words and a string chars.

A string is good if it can be formed by characters from chars (each character can only be used once).

Return the sum of lengths of all good strings in words.

 

Example 1:

Input: words = ["cat","bt","hat","tree"], chars = "atach"
Output: 6
Explanation: 
The strings that can be formed are "cat" and "hat" so the answer is 3 + 3 = 6.
Example 2:

Input: words = ["hello","world","leetcode"], chars = "welldonehoneyr"
Output: 10
Explanation: 
The strings that can be formed are "hello" and "world" so the answer is 5 + 5 = 10.
 

Note:

1 <= words.length <= 1000
1 <= words[i].length, chars.length <= 100
All strings contain lowercase English letters only.


"""

return sum(not cnt(w) - cnt(chars) and len(w) for w in words)
return sum([len(w) if (False not in [False if (w.count(l) > chars.count(l)) else True for l in [chr(c) for c in range(97, 123)]]) else 0 for w in words])

def countCharacters(self, words: List[str], chars: str) -> int:
    chars_cnt = collections.Counter(chars)
    ans = 0
    for word in words:
        word_cnt = collections.Counter(word)
        for c in word_cnt:
            if chars_cnt[c] < word_cnt[c]:
                break
        else:
            ans += len(word)
    return ans




def countCharacters(self, words: List[str], chars: str) -> int:
    ans = 0
    cnt = collections.Counter(chars)
    for w in words:
        c = collections.Counter(w)
        if all([c[i] <= cnt[i] for i in c]):
            ans += len(w)
    return ans



def countCharacters(self, words: List[str], chars: str) -> int:
    sum, ct = 0, collections.Counter
    chars_counter = ct(chars)
    for word in words:
        word_counter = ct(word)
        if all(word_counter[c] <= chars_counter[c] for c in word_counter):
            sum += len(word)
    return sum



def countCharacters(self, words: List[str], chars: str) -> int:
    counter = 0
    for w in words:
        included = True
        charsList = [c for c in chars]
        for c in w:
            if c in charsList:
                charsList.remove(c)
            else:
                included = False
                break
        if included: counter = counter+len(w)
    return counter













































































