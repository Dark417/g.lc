"""
680. Valid Palindrome II

Given a non-empty string s, you may delete at most one character. 
Judge whether you can make it a palindrome.

Example 1:
Input: "aba"
Output: True
Example 2:
Input: "abca"
Output: True
Explanation: You could delete the character 'c'.
Note:
The string will only contain lowercase characters a-z. The maximum length of the string is 50000.




"""


# dis
def validPalindrome(self, s):
    if s == s[::-1]:
        return True
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] == s[r]:
            l, r = l + 1, r - 1
        else:
            a = s[l + 1: r + 1]
            b = s[l:r]
            return a == a[::-1] or b == b[::-1]


# d
def vp(s):
    while len(s) > 1:
        if len(s) == 2:
            return True

        if s[0] != s[-1]:
            print(s)
            print(s[0])
            print(s[-1])

            if cp(s[:-1]) or cp(s[1:]):
                return True

    return True


def cp(s):
    while len(s) > 1:
        print(s)
        if len(s) == 2:
            if s[0] == s[1]:
                return True
            else:
                return False
        else:
            s = s[1:-1]
    return True


a = "aguokepatgbnvfqmgmlcupuufxoohdfpgjdmysgvhmvffcnqxjjxqncffvmhvgsymdjgpfdhooxfuupuculmgmqfvnbgtapekouga"
b = "ebcbbececabbacecbbcbe"
c = "cupuufxoohdfpgjdmysgvhmvffcnqxjjxqncffvmhvgsymdjgpfdhooxfuupucu"
res = vp(a)
# res = cp(b)
print(res)

# b = "eccer"
# #
# # print(b[-2])
