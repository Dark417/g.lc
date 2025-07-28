// # 266. 回文排列



public boolean canPermutePalindrome(String s) {
    int count = 0;
    for (char i = 0; i < 128 && count <= 1; i++) {
        int ct = 0;
        for (int j = 0; j < s.length(); j++) {
            if (s.charAt(j) == i)
                ct++;
        }
        count += ct % 2;
    }
    return count <= 1;
}




public boolean canPermutePalindrome(String s) {
    HashMap < Character, Integer > map = new HashMap < > ();
    for (int i = 0; i < s.length(); i++) {
        map.put(s.charAt(i), map.getOrDefault(s.charAt(i), 0) + 1);
    }
    int count = 0;
    for (char key: map.keySet()) {
         count += map.get(key) % 2;
    }
    return count <= 1;
}





public boolean canPermutePalindrome(String s) {
    int[] map = new int[128];
    for (int i = 0; i < s.length(); i++) {
        map[s.charAt(i)]++;
    }
    int count = 0;
    for (int key = 0; key < map.length && count <= 1; key++) {
        count += map[key] % 2;
    }
    return count <= 1;
}



public boolean canPermutePalindrome(String s) {
    int[] map = new int[128];
    int count = 0;
    for (int i = 0; i < s.length(); i++) {
        map[s.charAt(i)]++;
        if (map[s.charAt(i)] % 2 == 0)
            count--;
        else
            count++;
    }
    return count <= 1;
}




public boolean canPermutePalindrome(String s) {
    Set < Character > set = new HashSet < > ();
    for (int i = 0; i < s.length(); i++) {
        if (!set.add(s.charAt(i)))
            set.remove(s.charAt(i));
    }
    return set.size() <= 1;
}


