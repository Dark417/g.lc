# 567. 字符串的排列

# 
def checkInclusion(self, s1, s2):
    counter1 = collections.Counter(s1)
    N = len(s2)
    left = 0
    right = len(s1) - 1
    counter2 = collections.Counter(s2[0:right])
    while right < N:
        counter2[s2[right]] += 1
        if counter1 == counter2:
            return True
        counter2[s2[left]] -= 1
        if counter2[s2[left]] == 0:
            del counter2[s2[left]]
        left += 1
        right += 1
    return False




"""
public boolean checkInclusion(String s1, String s2) {
    int n = s1.length(), m = s2.length();
    if (n > m) {
        return false;
    }
    int[] cnt = new int[26];
    for (int i = 0; i < n; ++i) {
        --cnt[s1.charAt(i) - 'a'];
    }
    int left = 0;
    for (int right = 0; right < m; ++right) {
        int x = s2.charAt(right) - 'a';
        ++cnt[x];
        while (cnt[x] > 0) {
            --cnt[s2.charAt(left) - 'a'];
            ++left;
        }
        if (right - left + 1 == n) {
            return true;
        }
    }
    return false;
}



public boolean checkInclusion(String s1, String s2) {
    int n = s1.length(), m = s2.length();
    if (n > m) {
        return false;
    }
    int[] cnt1 = new int[26];
    int[] cnt2 = new int[26];
    for (int i = 0; i < n; ++i) {
        ++cnt1[s1.charAt(i) - 'a'];
        ++cnt2[s2.charAt(i) - 'a'];
    }
    if (Arrays.equals(cnt1, cnt2)) {
        return true;
    }
    for (int i = n; i < m; ++i) {
        ++cnt2[s2.charAt(i) - 'a'];
        --cnt2[s2.charAt(i - n) - 'a'];
        if (Arrays.equals(cnt1, cnt2)) {
            return true;
        }
    }
    return false;
}

每次窗口滑动时，只统计了一进一出两个字符，却比较了整个arr







public boolean checkInclusion(String s1, String s2) {
    char[] pattern = s1.toCharArray();
    char[] text = s2.toCharArray();

    int pLen = s1.length();
    int tLen = s2.length();

    int[] pFreq = new int[26];
    int[] winFreq = new int[26];

    for (int i = 0; i < pLen; i++) {
        pFreq[pattern[i] - 'a']++;
    }

    int pCount = 0;
    for (int i = 0; i < 26; i++) {
        if (pFreq[i] > 0){
            pCount++;
        }
    }

    int left = 0;
    int right = 0;
    // 当滑动窗口中的某个字符个数与 s1 中对应相等的时候才计数
    int winCount = 0;
    while (right < tLen){
        if (pFreq[text[right] - 'a'] > 0 ) {
            winFreq[text[right] - 'a']++;
            if (winFreq[text[right] - 'a'] == pFreq[text[right] - 'a']){
                winCount++;
            }
        }
        right++;

        while (pCount == winCount){
            if (right - left == pLen){
                return true;
            }
            if (pFreq[text[left] - 'a'] > 0 ) {
                winFreq[text[left] - 'a']--;
                if (winFreq[text[left] - 'a'] < pFreq[text[left] - 'a']){
                    winCount--;
                }
            }
            left++;
        }
    }
    return false;
}

"""












