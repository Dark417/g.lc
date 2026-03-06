# 825. 适龄的朋友

def numFriendRequests(self, ages: List[int]) -> int:
    n = len(ages)
    ages.sort()
    left = right = ans = 0
    for age in ages:
        if age < 15:
            continue
        while ages[left] <= 0.5 * age + 7:
            left += 1
        while right + 1 < n and ages[right + 1] <= age:
            right += 1
        ans += right - left
    return ans


def numFriendRequests(self, ages: List[int]) -> int:
    res = 0
    ages.sort()
    l = r = 0
    for age in ages:
        if age < 15:
            continue
        while ages[l] <= age * 0.5 + 7:
            l += 1
        while r < len(ages) and ages[r] <= age:
            r += 1
        res += r - l - 1
    return res


def numFriendRequests(self, ages: List[int]) -> int:
    cnts = [0] * (max(ages) + 1)
    for age in ages:
        cnts[age] += 1
    presum = [0] + list(accumulate(cnts))
    return sum(cnts[age] * max(0, presum[age + 1] - presum[age//2 + 8] - 1) for age in set(ages))



"""
public int numFriendRequests(int[] ages) {
    int n = ages.length;
    Arrays.sort(ages);
    int left = 0, right = 0, ans = 0;
    for (int age : ages) {
        if (age < 15) {
            continue;
        }
        while (ages[left] <= 0.5 * age + 7) {
            ++left;
        }
        while (right + 1 < n && ages[right + 1] <= age) {
            ++right;
        }
        ans += right - left;
    }
    return ans;
}



"""



def numFriendRequests(self, ages: List[int]) -> int:
    cnt = [0] * 121
    for age in ages:
        cnt[age] += 1
    pre = [0] * 121
    for i in range(1, 121):
        pre[i] = pre[i - 1] + cnt[i]
    
    ans = 0
    for i in range(15, 121):
        if cnt[i] > 0:
            bound = int(i * 0.5 + 7)
            ans += cnt[i] * (pre[i] - pre[bound ] - 1)
    return ans

"""
public int numFriendRequests(int[] ages) {
    int[] cnt = new int[121];
    for (int age : ages) {
        ++cnt[age];
    }
    int[] pre = new int[121];
    for (int i = 1; i <= 120; ++i) {
        pre[i] = pre[i - 1] + cnt[i];
    }
    int ans = 0;
    for (int i = 15; i <= 120; ++i) {
        if (cnt[i] > 0) {
            int bound = (int) (i * 0.5 + 8);
            ans += cnt[i] * (pre[i] - pre[bound - 1] - 1);
        }
    }
    return ans;
}



"""















