# 13. 罗马数字转整数

def romanToInt(self, s: str) -> int:
    translations = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000
    }
    number = 0
    s = s.replace("IV", "IIII").replace("IX", "VIIII")
    s = s.replace("XL", "XXXX").replace("XC", "LXXXX")
    s = s.replace("CD", "CCCC").replace("CM", "DCCCC")
    for char in s:
        number += translations[char]
    return number



def romanToInt(self, s: str) -> int:
	res = 0
	dc = {"I": 1,
          "V": 5,
          "X": 10,
          "L": 50,
          "C": 100,
          "D": 500,
          "M": 1000,
          "IV": 4,
          "IX": 9,
          "XL": 40,
          "XC": 90,
          "CD": 400,
          "CM": 900
         }
    pre = dc[s[0]]
    for i in range(1, len(s)):
    	n = dc[s[i]]
    	if pre < n:
    		res -= pre
    	else:
    		res += pre
    	pre = n
   	res += pre
   	return res



def romanToInt(self, s: str) -> int:
    d = {'I':1, 'IV':3, 'V':5, 'IX':8, 'X':10, 'XL':30, 'L':50, 'XC':80, 'C':100, 'CD':300, 'D':500, 'CM':800, 'M':1000}
    return sum(d.get(s[max(i-1, 0):i+1], d[n]) for i, n in enumerate(s))


















def romanToInt(self, s: str) -> int:
    dc = {"I": 1,
          "V": 5,
          "X": 10,
          "L": 50,
          "C": 100,
          "D": 500,
          "M": 1000,
          "IV": 4,
          "IX": 9,
          "XL": 40,
          "XC": 90,
          "CD": 400,
          "CM": 900
         }
    res = i = 0
    while i < len(s) - 1:
        if dc[s[i]] < dc[s[i + 1]]:
            res += dc[s[i:i+2]]
            i += 2
        else:
            res += dc[s[i]]
            i += 1
    return res if i == len(s) else res + dc[s[i]]




















