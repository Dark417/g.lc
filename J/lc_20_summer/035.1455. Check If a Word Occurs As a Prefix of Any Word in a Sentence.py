"""
035.1455. Check If a Word Occurs As a Prefix of Any Word in a Sentence
检查单词是否为句中其他单词的前缀


Given a sentence that consists of some words separated by a single space, and a searchWord.

You have to check if searchWord is a prefix of any word in sentence.

Return the index of the word in sentence where searchWord is a prefix of this word (1-indexed).

If searchWord is a prefix of more than one word, return the index of the first word (minimum index). 
If there is no such word return -1.

A prefix of a string S is any leading contiguous substring of S.

 

Example 1:

Input: sentence = "i love eating burger", searchWord = "burg"
Output: 4
Explanation: "burg" is prefix of "burger" which is the 4th word in the sentence.
Example 2:

Input: sentence = "this problem is an easy problem", searchWord = "pro"
Output: 2
Explanation: "pro" is prefix of "problem" which is the 2nd and the 6th word in the sentence, 
but we return 2 as it's the minimal index.
Example 3:

Input: sentence = "i am tired", searchWord = "you"
Output: -1
Explanation: "you" is not a prefix of any word in the sentence.
Example 4:

Input: sentence = "i use triple pillow", searchWord = "pill"
Output: 4
Example 5:

Input: sentence = "hello from the other side", searchWord = "they"
Output: -1
 

Constraints:

1 <= sentence.length <= 100
1 <= searchWord.length <= 10
sentence consists of lowercase English letters and spaces.
searchWord consists of lowercase English letters.

"""

# d
def isPrefixOfWord(self, sentence: str, searchWord: str) -> int:
    l = sentence.split()
    for i in range(len(l)):
        if l[i][:len(searchWord)] == searchWord:
            return i+1
    return -1


# d1
def isPrefixOfWord(self, sentence: str, searchWord: str) -> int:
    s = 1
    i = 0
    while i < len(sentence):
        tmp = ""
        while i < len(sentence):
            if sentence[i] != " ":
                tmp += sentence[i]
                i += 1
            else:
                break
        
        if tmp[:len(searchWord)] == searchWord:
            return s
        s += 1
        i += 1
    return -1
    

def isPrefixOfWord(self, sentence: str, searchWord: str) -> int:
    for i, w in enumerate(sentence.split(' '), 1):
        if w.startswith(searchWord):
            return i
    return -1


def isPrefixOfWord(self, sentence: str, searchWord: str) -> int:        
    it = (' ' + sentence).find(' ' + searchWord);        
    return -1 if it == -1 else sentence[:it].count(' ') + 1;



#
def split_iter(self, sentence: str):
        return (x.group(0) for x in re.finditer(r"[a-z]+", sentence))

def isPrefixOfWord(self, sentence: str, searchWord: str) -> int:        
    for i,w in enumerate(self.split_iter(sentence)):
        if w.startswith(searchWord):
            return i + 1
    return -1









