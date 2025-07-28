"""
A self-dividing number is a number that is divisible by every digit it contains.
For example, 128 is a self-dividing number because 128 % 1 == 0, 128 % 2 == 0, and 128 % 8 == 0.
Also, a self-dividing number is not allowed to contain the digit zero.
Given a lower and upper number bound, output a list of every possible self dividing number, including the bounds if possible.

Example 1:
Input:
left = 1, right = 22
Output: [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 22]
Note:
The boundaries of each input argument are 1 <= left <= right <= 10000.

"""



def selfDividingNumbers(self, left, right):
    ans = []
    isSelfDividing = True
    for i in range(left, right + 1):
        # single digit
        if i < 10:
            ans.append(i)
            # check if not contains 0, aka mod 10 != 0
        elif '0' not in str(i):
            for d in str(i):
                if i % int(d):
                    isSelfDividing = False
                    break
            if isSelfDividing:
                ans.append(i)

            isSelfDividing = True
    return ans

#brute force
def is_self_dividing(x):
    s = str(x)
    for d in s:
        if d=="0" or x%int(d)!=0:
            return False
    return True

def selfDividingNumbers(self, left, right):
    """
    :type left: int
    :type right: int
    :rtype: List[int]
    """
    ans = []
    for x in xrange(left, right+1):
        if is_self_dividing(x):
            ans.append(x)
    return ans



#D still buggy

def self_divide(left, right):

    result = []
    n = 1

    for i in range(left, right + 1):
        string = str(i)
        # print(i)
        if len(string) == 1:
            if string == "0":
                continue
            else:
                print("append ", i)
                result.append(int(string))
        else:
            for j in string:
                print("i ", i)

                if j != "0" and i % int(j) == 0:
                    print("n ", n)
                    if n == len(string):
                        result.append(i)
                        n = 1
                        break
                    else:
                        n += 1
                        print("n after i++", n)


    return result

result = self_divide(3, 22)
print(result)



