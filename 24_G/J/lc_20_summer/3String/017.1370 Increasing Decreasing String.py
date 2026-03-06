"""
017.1370 Increasing Decreasing String
上升下降字符串


Given a string s. You should re-order the string using the following algorithm:

Pick the smallest character from s and append it to the result.
Pick the smallest character from s which is greater than the last appended character to the result and append it.
Repeat step 2 until you cannot pick more characters.
Pick the largest character from s and append it to the result.
Pick the largest character from s which is smaller than the last appended character to the result and append it.
Repeat step 5 until you cannot pick more characters.
Repeat the steps from 1 to 6 until you pick all characters from s.
In each step, If the smallest or the largest character appears more than once you can choose any occurrence and append it to the result.

Return the result string after sorting s with this algorithm.

 

Example 1:

Input: s = "aaaabbbbcccc"
Output: "abccbaabccba"
Explanation: After steps 1, 2 and 3 of the first iteration, result = "abc"
After steps 4, 5 and 6 of the first iteration, result = "abccba"
First iteration is done. Now s = "aabbcc" and we go back to step 1
After steps 1, 2 and 3 of the second iteration, result = "abccbaabc"
After steps 4, 5 and 6 of the second iteration, result = "abccbaabccba"
Example 2:

Input: s = "rat"
Output: "art"
Explanation: The word "rat" becomes "art" after re-ordering it with the mentioned algorithm.
Example 3:

Input: s = "leetcode"
Output: "cdelotee"
Example 4:

Input: s = "ggggggg"
Output: "ggggggg"
Example 5:

Input: s = "spo"
Output: "ops"
 

Constraints:

1 <= s.length <= 500
s contains only lower-case English letters.



"""

def sortString(self, s: str) -> str:
    cnt, ans, asc = collections.Counter(s), [], True
    while cnt:                                                                  # if Counter not empty.
        for c in sorted(cnt.keys()) if asc else reversed(sorted(cnt.keys())):   # traverse keys in ascending/descending order.
            ans.append(c)                                                       # append the key.
            cnt[c] -= 1                                                         # decrease the count.
            if cnt[c] == 0:                                                     # if the count reaches to 0.
                del cnt[c]                                                      # remove the key from the Counter.
        asc = not asc                                                           # change the direction, same as asc ^= True.
    return ''.join(ans)


def sortString(self, s: str) -> str:
    cnt, ans, asc  = collections.Counter(s), [], True
    while len(ans) < len(s):                                # if not finish.
        for i in range(26):                                 # traverse lower case letters.
            c = string.ascii_lowercase[i if asc else ~i]    # in ascending/descending order.
            if cnt[c] > 0:                                  # if the count > 0.
                ans.append(c)                               # append the character.
                cnt[c] -= 1                                 # decrease the count.
        asc = not asc                                       # change direction.
    return ''.join(ans)


def sortString(self, s: str) -> str:
    counter, result = collections.Counter(s), []
    while counter:
        for traverse in string.ascii_lowercase, reversed(string.ascii_lowercase):
            result += [c for c in traverse if c in counter]
            counter -= dict.fromkeys(counter, 1)
    return ''.join(result)


def sortString(self, s: str) -> str:

    result = []
    counter = collections.Counter(s)

    while len(result) < len(s):
        for sequence in [string.ascii_lowercase, string.ascii_lowercase[::-1]]:
            for ch in sequence:
                if counter[ch] > 0:
                    result.append(ch)
                    counter[ch] -= 1

    return "".join(result)






















































