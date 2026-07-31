# 475. 供暖器


def findRadius(self, houses: List[int], heaters: List[int]) -> int:
    ans = 0
    heaters.sort()
    for house in houses:
        j = bisect_right(heaters, house)
        i = j - 1
        rightDistance = heaters[j] - house if j < len(heaters) else float('inf')
        leftDistance = house - heaters[i] if i >= 0 else float('inf')
        curDistance = min(leftDistance, rightDistance)
        ans = max(ans, curDistance)
    return ans

"""
public int findRadius(int[] houses, int[] heaters) {
    int ans = 0;
    Arrays.sort(heaters);
    for (int house : houses) {
        int i = binarySearch(heaters, house);
        int j = i + 1;
        int leftDistance = i < 0 ? Integer.MAX_VALUE : house - heaters[i];
        int rightDistance = j >= heaters.length ? Integer.MAX_VALUE : heaters[j] - house;
        int curDistance = Math.min(leftDistance, rightDistance);
        ans = Math.max(ans, curDistance);
    }
    return ans;
}

public int binarySearch(int[] nums, int target) {
    int left = 0, right = nums.length - 1;
    if (nums[left] > target) {
        return -1;
    }
    while (left < right) {
        int mid = (right - left + 1) / 2 + left;
        if (nums[mid] > target) {
            right = mid - 1;
        } else {
            left = mid;
        }
    }
    return left;
}
"""



def findRadius(self, houses: List[int], heaters: List[int]) -> int:
    ans = 0
    houses.sort()
    heaters.sort()
    j = 0
    for i, house in enumerate(houses):
        curDistance = abs(house - heaters[j])
        while j + 1 < len(heaters) and abs(houses[i] - heaters[j]) >= abs(houses[i] - heaters[j + 1]):
            j += 1
            curDistance = min(curDistance, abs(houses[i] - heaters[j]))
        ans = max(ans, curDistance)
    return an




"""
public int findRadius(int[] houses, int[] heaters) {
    Arrays.sort(houses);
    Arrays.sort(heaters);
    int ans = 0;
    for (int i = 0, j = 0; i < houses.length; i++) {
        int curDistance = Math.abs(houses[i] - heaters[j]);
        while (j < heaters.length - 1 && Math.abs(houses[i] - heaters[j]) >= Math.abs(houses[i] - heaters[j + 1])) {
            j++;
            curDistance = Math.min(curDistance, Math.abs(houses[i] - heaters[j]));
        }
        ans = Math.max(ans, curDistance);
    }
    return ans;
}
"""





































