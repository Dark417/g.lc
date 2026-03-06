"""
046.1433 Check If a String Can Break Another String
检查一个字符串是否可以打破另一个字符串

Given two strings: s1 and s2 with the same size, check if some permutation of string s1 can break some permutation of string s2 or vice-versa (in other words s2 can break s1).

A string x can break string y (both of size n) if x[i] >= y[i] (in alphabetical order) for all i between 0 and n-1.

 

Example 1:

Input: s1 = "abc", s2 = "xya"
Output: true
Explanation: "ayx" is a permutation of s2="xya" which can break to string "abc" which is a permutation of s1="abc".
Example 2:

Input: s1 = "abe", s2 = "acd"
Output: false 
Explanation: All permutations for s1="abe" are: "abe", "aeb", "bae", "bea", "eab" and "eba" and all permutation for s2="acd" are: "acd", "adc", "cad", "cda", "dac" and "dca". However, there is not any permutation from s1 which can break some permutation from s2 and vice-versa.
Example 3:

Input: s1 = "leetcodee", s2 = "interview"
Output: true
 

Constraints:

s1.length == n
s2.length == n
1 <= n <= 10^5
All strings consist of lowercase English letters.



"""


def checkIfCanBreak(self, s1: str, s2: str) -> bool:
    l1, l2 = sorted(s1), sorted(s2)
    l = 0
    for i in range(len(s1)):
        if l1[i] >= l2[i]:
            l += 1
    if l == len(s1):
        return True
    else:
        l = 0
        for i in range(len(s1)):
            if l1[i] <= l2[i]:
                l += 1
        if l == len(s1):
            return True
        else:
            return False


def check(self, d1, d2):
    s = 0
    for c in 'abcdefghijklmnopqrstuvwxyz':
        s += d1[c] - d2[c]
        if s < 0:
            return False
    return True
    
def checkIfCanBreak(self, s1: str, s2: str) -> bool:
    d1 = collections.Counter(s1)
    d2 = collections.Counter(s2)
    return self.check(d1, d2) | self.check(d2, d1)

#lee215
	#p2; cmp not defined in p3
    return not {1, -1}.issubset(set(cmp(a, b) for a, b in zip(sorted(s1), sorted(s2))))
	return not {(True,True),(False,False)}.issubset(set((a >= b, a > b) for a, b in zip(sorted(s1), sorted(s2))))


	return all(x <= y for x, y in zip(*sorted([sorted(s1), sorted(s2)])))

	A1, A2 = sorted(s1), sorted(s2)
    return all([a >= b for a, b in zip(A1, A2)]) or all([a <= b for a, b in zip(A1, A2)])




    