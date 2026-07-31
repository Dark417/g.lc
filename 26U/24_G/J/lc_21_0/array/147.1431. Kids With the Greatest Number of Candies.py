"""
1431. Kids With the Greatest Number of Candies
拥有最多糖果的孩子


"""

def kidsWithCandies(self, candies: List[int], extraCandies: int) -> List[bool]:
    maxCandies = max(candies)
    ret = [candy + extraCandies >= maxCandies for candy in candies]
    return ret

    return [candy + extraCandies >= maxCandies for candy in candies]

return [True if candies[i] + extraCandies>= max(candies) else False for i in range(len(candies))]














































