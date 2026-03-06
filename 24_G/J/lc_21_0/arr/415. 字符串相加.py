# 415. 字符串相加

# return str(int(num1)+int(num2))

	i = len(num1) - 1
	j = len(num2) - 1
	add = 0
	ans = ""

	while i >= 0 or j >= 0 or car != 0:
		val = car

		if i >= 0:
			i -= 1
			val += int(num1[i])

		if j >= 0:
			j -= 1
			val += int(num2[j])

		car, val = divmod(val, 10)
		ans += str(val)

		# ans.append(val)
		# add = val/10
	return ans



def addStrings(self, num1, num2):
    z = itertools.izip_longest(num1[::-1], num2[::-1], fillvalue='0')
    res, carry, zero2 = [], 0, 2*ord('0')
    for i in z:
        cur_sum = ord(i[0]) + ord(i[1]) - zero2 + carry
        res.append(str(cur_sum % 10))
        carry = cur_sum // 10
    return ('1' if carry else '') + ''.join(res[::-1])



def addStrings(self, num1, num2):
	return str(
		reduce(lambda a, b: 10*a + b, 
		 map(lambda x: ord(x[0])+ord(x[1])-2*ord('0'),
		   list(itertools.izip_longest(num1[::-1], num2[::-1], fillvalue='0'))[::-1]
		 ) 
		)
		)


def addStrings(self, num1: str, num2: str) -> str:
    res = ""
    i, j, carry = len(num1) - 1, len(num2) - 1, 0
    while i >= 0 or j >= 0:
        n1 = int(num1[i]) if i >= 0 else 0
        n2 = int(num2[j]) if j >= 0 else 0
        tmp = n1 + n2 + carry
        carry = tmp // 10
        res = str(tmp % 10) + res
        i, j = i - 1, j - 1
    return "1" + res if carry else res


        
def addStrings(self, num1: str, num2: str) -> str:
    i, j, carry, ans = len(num1) - 1, len(num2) - 1, 0, ""

    while i >= 0 or j >= 0 or carry:
        val = carry

        if i >= 0: i, val = i - 1, val + int(num1[i])
        if j >= 0: j, val = j - 1, val + int(num2[j])

        carry, val = divmod(val, 10)
        ans = str(val) + ans
    
    return ans


'''
class Solution {
    public String addStrings(String num1, String num2) {
        int i = num1.length() - 1, j = num2.length() - 1, add = 0;
        StringBuffer ans = new StringBuffer();
        while (i >= 0 || j >= 0 || add != 0) {
            int x = i >= 0 ? num1.charAt(i) - '0' : 0;
            int y = j >= 0 ? num2.charAt(j) - '0' : 0;
            int result = x + y + add;
            ans.append(result % 10);
            add = result / 10;
            i--;
            j--;
        }
        // 计算完以后的答案需要翻转过来
        ans.reverse();
        return ans.toString();
    }
}

'''
