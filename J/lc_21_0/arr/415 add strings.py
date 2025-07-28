def addStrings( num1, num2):
        """
        :type num1: str
        :type num2: str
        :rtype: str
        """
        num1, num2 = list(num1), list(num2)
        print num1
        print num2


        carry, res = 0, []
        a1, a2 = "", ""
        # a3 = 0

        while len(num2) > 0 or len(num1) > 0:

            
            # a2 = 
            # a3 = a1-a2
            n1 = ord(num1.pop())-ord('0') if len(num1) > 0 else 0
            print 
            print n1
            print ord('0')
            

            n2 = ord(num2.pop())-ord('0') if len(num2) > 0 else 0
            print n2

            temp = n1 + n2 + carry
            print temp

            res.append(temp % 10)
            print res

            carry = temp // 10
            print carry
            print

        if carry: res.append(carry)
        return ''.join([str(i) for i in res])[::-1]


x = addStrings( "123","456")

print x

