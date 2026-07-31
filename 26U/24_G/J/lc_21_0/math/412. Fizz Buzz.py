# 412. Fizz Buzz



def fizzBuzz(self, n: int) -> List[str]:
    return ["FizzBuzz" if i%15==0 else "Fizz" if i%3==0 else "Buzz" if i%5==0 else str(i) for i in range(1, n + 1)]



def fizzBuzz(self, n):
    ans = []
    for num in range(1,n+1):
        divisible_by_3 = (num % 3 == 0)
        divisible_by_5 = (num % 5 == 0)
        num_ans_str = ""
        if divisible_by_3:
            num_ans_str += "Fizz"
        if divisible_by_5:
            num_ans_str += "Buzz"
        if not num_ans_str:
            num_ans_str = str(num)
		ans.append(num_ans_str)  

    return ans


def fizzBuzz(self, n):
	ans = []
	fizz_buzz_dict = {3 : "Fizz", 5 : "Buzz"}
    for num in range(1,n+1):
        num_ans_str = ""
        for key in fizz_buzz_dict.keys():
			if num % key == 0:
            	num_ans_str += fizz_buzz_dict[key]
		if not num_ans_str:
            num_ans_str = str(num)

        ans.append(num_ans_str)  
    return ans









