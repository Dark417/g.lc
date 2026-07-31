class Solution
{
    public int countGoodSubstrings(String s) {
        int n = s.length();
        int res = 0;
        int left = 0, right = 0;
        HashMap<Character, Integer> window = new HashMap<>();
        while (right < n) {
            char r = s.charAt(right++);
            window.put(r, window.getOrDefault(r, 0) + 1);

            while (right - left == 3) {
                if (window.entrySet().stream().parallel().filter(e -> e.getValue() == 1).count() == 3) res++;
                char l = s.charAt(left++);
                window.put(l, window.get(l) - 1);
            }
        }
        return res;
    }
}


class Solution {
    public int countGoodSubstrings(String s) {
        Map<Character,Integer> map = new HashMap<>();
        int len = s.length();
        if(len < 3){return 0;}
        int result = 0;
        map.put(s.charAt(0), 1);
        map.put(s.charAt(1), map.getOrDefault(s.charAt(1), 0)+1);
        map.put(s.charAt(2), map.getOrDefault(s.charAt(2), 0)+1);
        if(map.size() == 3){result++;}
        for(int i = 3; i < len; i++){
            map.put(s.charAt(i), map.getOrDefault(s.charAt(i), 0)+1);
            int number = map.get(s.charAt(i-3));
            if(number == 1){map.remove(s.charAt(i-3));}
            else{map.put(s.charAt(i-3), number-1);}
            if(map.size() == 3){result++;}
        }
        return result;
    }
}


class Solution {
    public int countGoodSubstrings(String s) {
        int ans=0;
        for(int i=0;i<s.length()-2;i++){if(s.charAt(i)!=s.charAt(i+1)&&s.charAt(i)!=s.charAt(i+2)&&s.charAt(i+1)!=s.charAt(i+2)){ans++;}}
        return ans;
    }
}






// # 1984. 学生分数的最小差值
class Solution {
    public int minimumDifference(int[] nums, int k) {
        numssorted = nums.sort();
        int mn = 999;
        for (int i = 0, i < nums.length-k+1, i++) {
            int curmin = nums[i+k-1] - nums[i];
            mn = min(curmin, mn);
        }
        return mn;
    }
}

// official
class Solution {
    public int minimumDifference(int[] nums, int k) {
        int n = nums.length;
        Arrays.sort(nums);
        int ans = Integer.MAX_VALUE;
        for (int i = 0; i + k - 1 < n; ++i) {
            ans = Math.min(ans, nums[i + k - 1] - nums[i]);
        }
        return ans;
    }
}

class Solution {
    public int minimumDifference(int[] nums, int k) {
        Arrays.sort(nums);
        int res = Integer.MAX_VALUE;
        for (int l = 0, r = k - 1; r < nums.length; )
            res = Math.min(res, nums[r++] - nums[l++]);
        return res;
    }
}

public int minimumDifference(int[] nums, int k) {
    if(k < 2) return 0;
    Arrays.sort(nums);
    int min = Integer.MAX_VALUE, bdry = k-1;
    for(int i = nums.length-1; i >= bdry; --i) 
        min = Math.min(min, nums[i] - nums[i-k+1]);
    return min; 
}


// # 1176. 健身计划评估

public int dietPlanPerformance(int[] calories, int k, int lower, int upper) {
    int res = 0;
    int sm = 0;
    for (int i=0; i<k; i++) {
        sm += calories[i];
    }
    if (sm > upper) {
        res += 1;
    }
    if (sm < lower) {
        res -= 1;
    }
    for (int i = k; i < calories.length; i++) {
        sm += calories[i] - calories[i - k];
        if (sm > upper) {
        res += 1;
        }
        if (sm < lower) {
            res -= 1;
        }
    }
    return res;
}







