"""
Given a positive integer num consisting only of digits 6 and 9.

Return the maximum number you can get by changing at most one digit (6 becomes 9, and 9 becomes 6).

Example 1:

Input: num = 9669
Output: 9969
Explanation:
Changing the first digit results in 6669.
Changing the second digit results in 9969.
Changing the third digit results in 9699.
Changing the fourth digit results in 9666.
The maximum number is 9969.
Example 2:

Input: num = 9996
Output: 9999
Explanation: Changing the last digit 6 to 9 results in the maximum number.
Example 3:

Input: num = 9999
Output: 9999
Explanation: It is better not to apply any change.

Constraints:

1 <= num <= 10^4
num's digits are 6 or 9.

"""


def maximum69Number(self, num: int) -> int:
    i = 0
    tem = num
    sixidx = -1
    while tem > 0:
        if tem % 10 == 6:
            sixidx = i  # refresh sixidx when found 6 at large digit.
        tem = tem // 10
        i += 1
    return (num + 3 * (10 ** sixidx)) if sixidx != -1 else num


def maximum69Number(self, num):
    return int(str(num).replace('6', '9', 1))
    return str(num).replace('6', '9', 1)

#D
def maximum69Number(self, num):
    """
    :type num: int
    :rtype: int
    """
    num1 = str(num)
    i = 0

    while i < len(num1):
        if num1[i] == '9':
            i += 1
            continue
        else:
            num1 = num1[:i] + '9' + num1[i + 1:]
            result = int(num1)
            return result

    return int(num1)