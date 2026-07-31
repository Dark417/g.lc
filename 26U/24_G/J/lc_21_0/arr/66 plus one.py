# [1,2,3] -> [1,2,4]

digits = [1,2,3,9]

def plusOne(digits):

	if digits[len(digits)-1] == 9:
		digits[len(digits)-1] = 1
		digits.append(0)

	else:
		digits[len(digits)-1]+= 1

	return digits


def test(digits):
	result = []
    str_digits = ''.join(str(i) for i in digits)
    int_digits = int(str_digits) + 1
    str_digits = str(int_digits)
    for i in str_digits:
       result.append(int(i))
    return result

x = test(digits)
print x