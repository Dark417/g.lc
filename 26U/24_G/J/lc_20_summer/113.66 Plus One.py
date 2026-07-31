"""
113.66 Plus One 



Given a non-empty array of digits representing a non-negative integer, plus one to the integer.

The digits are stored such that the most significant digit is at the head of the 
ist, and each element in the array contain a single digit.

You may assume the integer does not contain any leading zero, except the number 0 itself.

Example 1:

Input: [1,2,3]
Output: [1,2,4]
Explanation: The array represents the integer 123.
Example 2:

Input: [4,3,2,1]
Output: [4,3,2,2]
Explanation: The array represents the integer 4321.



"""


# D
# 0
def plusOne(self, digits: List[int]) -> List[int]:
    s = "".join(str(i) for i in digits)
    i = int(s)+1
    l = list(int(i) for i in str(i))
    return l

    return map(int, list(str(int(''.join(map(str, digits))) + 1)))
    return [int(a) for a in (str(int(''.join(map(str, digits))) + 1))]





def plusOne(digits):
    num = 0
    for i in range(len(digits)):
    	num += digits[i] * pow(10, (len(digits)-1-i))
    return [int(i) for i in str(num+1)]


def plusOne(digits):
    num = sum(10**i * n for i, n in enumerate(digits[::-1]))
    return [int(n) for n in str(num+1)]




def plusOne(self, digits: List[int]) -> List[int]:
    for i in range(len(digits)-1, -1, -1):
        if digits[i] != 9:
            digits[i] += 1
            return digits
        digits[i] = 0
    return [1] + digits




def plusOne(self, digits: List[int]) -> List[int]:
    newlst = []
    while digits and digits[-1] == 9:
        digits.pop()
        newlst.append(0)
    if not digits:
        return [1] + newlst
    else:
        digits[-1] += 1
        return digits + newlst




def plusOne(self, digits):
    if len(digits) == 1 and digits[0] == 9:
        return [1, 0]

    if digits[-1] != 9:
        digits[-1] += 1
        return digits
    else:
        digits[-1] = 0
        digits[:-1] = self.plusOne(digits[:-1])
        return digits  




def plusOne(self, digits):
    if len(digits) == 0:
        digits = [1]
    elif digits[-1] == 9:
        digits = self.plusOne(digits[:-1])
        digits.extend([0])
    else:
        digits[-1] += 1
    return digits




def plusOne(self, digits):
    if digits[-1] < 9:
        digits[-1] += 1
    elif digits[-1] == 9:
        digits[-1] = 0
        if len(digits) == 1:
            digits.insert(0, 1)
        else:
            digits[:-1] = self.plusOne(digits[:-1])
    return digits




def plusOne(self, digits):
    if digits == []:  #just for case: digits = [9]
        return [1]
    if digits[-1] != 9:
        return digits[:-1]+[digits[-1]+1]
    else:
        return self.plusOne(digits[:-1])+[0]



def plusOne(self, digits):
    digits = digits or [0]
    last = digits.pop()
    
    if last == 9:
        return self.plusOne(digits) + [0]
    else:
        return digits + [last + 1]



def plusOne(digits):
    digits[-1] += 1
    for i in range(len(digits)-1, 0, -1):
        if digits[i] != 10:
            break
        digits[i] = 0
        digits[i-1] += 1
    
    if digits[0] == 10:
        digits[0] = 0
        return [1] + digits
    return digits



def plusOne(self, digits: List[int]) -> List[int]:
    for index in range(len(digits)-1, -1, -1):
        digits[index] += 1
        if digits[index] != 10:
            return digits
        digits[index] = 0
    return [1] + digits



def plusOne(self, digits):
    for i in range(len(digits)):
        if digits[~i] < 9:
            digits[~i] += 1
            return digits
        digits[~i] = 0
    return [1] + [0] * len(digits)



def plusOne(self, digits):
    length = len(digits) - 1
    while digits[length] == 9:
        digits[length] = 0
        length -= 1
    if(length < 0):
        digits = [1] + digits
    else:
        digits[length] += 1
    return digits


def plusOne(self, digits):
    length = len(digits)
    for i in range(length-1, -1, -1):
        num = digits[i] + 1
        if num > 9:
            digits[i] = 0
            if i == 0:
                digits = [1] + digits
        else:
            digits[i] += 1
            break
            
    return digits


def plusOne(self, digits):
    num=reduce(lambda x,y:x*10+y,nums)+1
    return [int(i) for i in str(num)]




def plusOne(self, digits: List[int]) -> List[int]:
   digits[-1] += 1
   if digits[-1]  == 10:
       try:   # same as if digits != []
           digits = self.plusOne(digits[:-1]) + [0]
       except:
           digits = [1, 0]
   return digits


def plusOne(self, digits):
    if digits == []:  #just for case: digits = [9]
        return [1]
    if digits[-1] != 9:
        return digits[:-1]+[digits[-1]+1]
    else:
        return self.plusOne(digits[:-1])+[0]


def plusOne(self, digits):
    digits = digits or [0]
    last = digits.pop()
    
    if last == 9:
        return self.plusOne(digits) + [0]
    else:
        return digits + [last + 1]



def plusOne(self, digits):
    if digits == []:
        digits = [0] + digits
        
    if digits[-1] == 9:
        digits = self.plusOne(digits[:-1]) + [0]
    else: 
        digits[-1] += 1
        
    return digits




def plusOne(self, digits):
    if len(digits)==0:
        return False
    addCarry=1
    for i in range(len(digits)-1,-1,-1):
        digits[i]+=addCarry
        if digits[i]==10:
            digits[i]=0
            if i==0:
                digits.insert(0,1)
        else:
            break
    return digits


def plusOne(self, digits):
    for i in range(len(digits)-1, -1, -1):
        a = (digits[i]+1) // 10
        digits[i] = (digits[i]+1) % 10
        if a == 0: return digits
    if a == 1:
        digits.insert(0, 1)
    return digits




def plusOne(self, digits):
    if digits[-1] != 9:
         digits[-1] += 1
         return digits
    i = -1
    while i >= -len(digits) and digits[i] == 9:
         digits[i] = 0
         i -= 1
    if i == -len(digits)-1:
         digits.insert(0, 1)
    else:
        digits[i] +=1
    return digits



def plusOne(self, digits):
    carry = 1
    for i, d in enumerate(digits[::-1]):
        carry, digits[~i] = divmod(digits[~i] + carry, 10)
    if carry:
        digits = [carry] + digits
    return digits





def plusOne(self, digits: List[int]) -> List[int]:
    num = 1
    for i in range(len(digits)):
        num += digits[::-1][i] * 10 ** i
        
    return [int(i) for i in str(num)]


def plusOne(self, digits: List[int]) -> List[int]:
    if digits[-1] < 9:
        digits[-1] += 1            
        return digits
    num = 1
    for exponent, ea in enumerate(digits[::-1]):
        num += ea * pow(10, exponent)
    return [int(ea) for ea in str(num)]

















