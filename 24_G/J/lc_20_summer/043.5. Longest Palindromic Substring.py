"""
043.5. Longest Palindromic Substring
最长回文子串

Given a string s, find the longest palindromic substring in s. You may assume that the maximum length of s is 1000.

Example 1:

Input: "babad"
Output: "bab"
Note: "aba" is also a valid answer.
Example 2:

Input: "cbbd"
Output: "bb"









"""


# longest palindrome subsequence
def longestPalindrome(self, s: str) -> str:
        if len(s) <= 1:
            return s 
        if s[0] == s[-1]:
            lp = s[0] + self.longestPalindrome(s[1:-1]) + s[-1]
        else:
            if len(self.longestPalindrome(s[:-1])) > len(self.longestPalindrome(s[1:])):
                lp = self.longestPalindrome(s[:-1])
            else:
                lp = self.longestPalindrome(s[1:])
        return lp





        