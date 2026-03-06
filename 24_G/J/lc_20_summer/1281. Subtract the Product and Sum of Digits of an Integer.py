"""
1281. Subtract the Product and Sum of Digits of an Integer
Given an integer number n, return the difference between the product of its digits and the sum of its digits.

Example 1:

Input: n = 234
Output: 15
Explanation:
Product of digits = 2 * 3 * 4 = 24
Sum of digits = 2 + 3 + 4 = 9
Result = 24 - 9 = 15
Example 2:

Input: n = 4421
Output: 21
Explanation:
Product of digits = 4 * 4 * 2 * 1 = 32
Sum of digits = 4 + 4 + 2 + 1 = 11
Result = 32 - 11 = 21

Constraints:

1 <= n <= 10^5
"""
input = 234
result = subtractProductAndSum(_, input)
print(result)

input = 234

def ra(self, n: int) -> int:
    return n

print(ra(_, input))

def subtractProductAndSum(self, n: int) -> int:
    a = [int(x) for x in str(n)]
    return np.prod(a) - np.sum(a)

#32
def subtractProductAndSum(self, n):
    dm = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
    s = repr(n)
    sm, pr = 0, 1
    for c in s:
        pr *= dm[c]
        sm += dm[c]
    return pr - sm

#44
def subtractProductAndSum(self, n):
    lis = map(int, list(str(n)))
    return reduce(lambda x, y: x * y, lis) - sum(lis)

#24
def subtractProductAndSum(self, n: int) -> int:
    sum, prod = 0, 1
    while n:
        n, digit = divmod(n, 10)
        sum += digit
        prod *= digit
    return prod - sum

#28
def subtractProductAndSum(self, n: int) -> int:
    sum, prod = 0, 1
    while n:
        digit = n % 10
        sum += digit
        prod *= digit
        n //= 10
    return prod - sum



#24ms
def subtractProductAndSum(self, n):
    A = map(int, str(n))
    # A = list(map(int, str(n))) #alternative
    return reduce(operator.mul, A) - sum(A)




#D
def diff_pdt_sum(n):

    pdt = 1
    summ = 0

    str_ = str(n)
    for i in str_:
        pdt = pdt * int(i)
        summ = summ + int(i)
    diff = pdt - summ
    return diff

result = diff_pdt_sum(input)
print(result)

result = subtractProductAndSum(_, input)
print(result)