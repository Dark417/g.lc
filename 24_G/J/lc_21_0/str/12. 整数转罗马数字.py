# 12. 整数转罗马数字


def intToRoman(self, num: int) -> str:
    d = {1000: 'M', 900: 'CM', 500: 'D', 400: 'CD', 100: 'C', 90: 'XC', 50: 'L', 40: 'XL', 10: 'X', 9: 'IX', 5: 'V', 4: 'IV', 1: 'I'}
    res = ''
    for k in d:
        while num >= k:
            res += d[k]
            num -= k
    return res
        

digits = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), 
          (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

def intToRoman(self, num: int) -> str:
    roman_digits = []
    # Loop through each symbol.
    for value, symbol in digits:
        # We don't want to continue looping if we're done.
        if num == 0: break
        count, num = divmod(num, value)
        # Append "count" copies of "symbol" to roman_digits.
        roman_digits.append(symbol * count)
    return "".join(roman_digits)



def intToRoman(self, num: int) -> str:
    nums = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    romans = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]

    index = 0
    res = ''
    while index < 13:
        # 注意：这里是等于号，表示尽量使用大的"面值"
        while num >= nums[index]:
            res += romans[index]
            num -= nums[index]
        index += 1
    return res





















