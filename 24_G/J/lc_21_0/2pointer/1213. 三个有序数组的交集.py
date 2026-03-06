# 1213. 三个有序数组的交集


"""
1 Counting
List
public List<Integer> arraysIntersection(int[] arr1, int[] arr2, int[] arr3) {
    List<Integer> list = new ArrayList<>();
    int[] arr = new int[2001];
    for(int i:arr1) arr[i]++;
    for(int i:arr2) arr[i]++;
    for(int i:arr3){
        if(arr[i]==2)   list.add(i);
    }
    return list;
}


HashMap
public List<Integer> arraysIntersection(int[] arr1, int[] arr2, int[] arr3) {
    List<Integer> list = new ArrayList<>();
    Map<Integer, Integer> map = new HashMap<>();
    for(int i:arr1) map.put(i, map.getOrDefault(i, 0)+1);
    for(int i:arr2) map.put(i, map.getOrDefault(i, 0)+1);
    for(int i:arr3) {
        if(map.containsKey(i) && map.get(i) == 2)   list.add(i);
    }
    return list;
}





方法二：用双指针 两两比较
public List<Integer> arraysIntersection(int[] arr1, int[] arr2, int[] arr3) {
        List<Integer> list = new ArrayList<>();
        int[] res = intersect(intersect(arr1, arr2), arr3);
        for(int i:res)  list.add(i);
        return list;
    }
    int[] intersect(int[] arr1, int[] arr2){
        int i = 0, j = 0, index = 0;
        while(i<arr1.length && j<arr2.length){
            if(arr1[i]<arr2[j]){
                i++;
            }else if(arr2[j]<arr1[i]){
                j++;
            }else{
                arr1[index++] = arr1[i];
                i++;
                j++;
            }
        }
        return Arrays.copyOfRange(arr1, 0, index);
    }








方法三：三指针，每次最小的元素的index后移
public List<Integer> arraysIntersection(int[] arr1, int[] arr2, int[] arr3) {
    List<Integer> list = new ArrayList<>();
    int i = 0, j = 0, k = 0;
    int minValue = 0;
    while(i < arr1.length && j < arr2.length && k < arr3.length){
        if(arr1[i] == arr2[j] && arr2[j] == arr3[k]){
            list.add(arr1[i]);
            i++;
            j++;
            k++;
        }else{
            minValue = Math.min(Math.min(arr1[i], arr2[j]), arr3[k]);
            if(arr1[i] == minValue) i++;
            if(arr2[j] == minValue) j++;
            if(arr3[k] == minValue) k++;
        }
    }
    return list;
}




方法四：由于原数组有序，容易联想到二分查找法
public List<Integer> arraysIntersection(int[] arr1, int[] arr2, int[] arr3) {
    List<Integer> list = new ArrayList<>();
    
    for(int i:arr1) {
        if(binarySearch(arr2, i) && binarySearch(arr3, i)){
            list.add(i);
        }
    }
    return list;
}
boolean binarySearch(int[] arr, int num){
    int l = 0, r = arr.length - 1, mid = 0;
    while(l <= r){
        mid = l + (r - l)/2;
        if(arr[mid] == num) return true;
        else if(arr[mid] < num) l = mid + 1;
        else r = mid - 1;
    }
    return false;
}



方法五：比较直接，用两个set两两求交集
public List<Integer> arraysIntersection(int[] arr1, int[] arr2, int[] arr3) {
    List<Integer> list = new ArrayList<>();
    Set<Integer> set1 = new HashSet<>();
    Set<Integer> set2 = new HashSet<>();
    for(int i:arr1) set1.add(i);
    for(int i:arr2) {
        if(set1.contains(i))    set2.add(i);
    }
    for(int i:arr3){
        if(set2.contains(i))   list.add(i);
    }
    return list;
}





"""