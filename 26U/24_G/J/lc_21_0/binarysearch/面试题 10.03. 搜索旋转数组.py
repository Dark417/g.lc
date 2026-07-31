# 面试题 10.03. 搜索旋转数组

"""
public int search(int[] arr, int target) {
    if(arr[0]==target)
        return 0;
    int l=0;
    int r=arr.length-1;
    int mid=0;
    while(l<=r){
        mid=l+(r-l)/2;
        if(arr[mid]==target){
            while(mid>0&&arr[mid-1]==arr[mid])  mid--;
            return mid;
        }
        if(arr[mid]<arr[r]){
            if(arr[mid]<target&&target<=arr[r]) l=mid+1;
            else    r=mid-1;
        }
        else if(arr[mid]>arr[r]){
            if(arr[l]<=target&&target<arr[mid]) r=mid-1;
            else l=mid+1;
        }
        //arr[mid]==arr[r]说明要么r~0~mid都相等，要么mid~r都相等，无论哪种r 都可以舍去
        else{
            r--;
        }
    }
    return -1;
}

"""


def search(self, arr: List[int], target: int) -> int:
    n=len(arr)
    left=0
    right=n-1
    while left<=right:
        if arr[left]==target:
            return left
        mid=left+(right-left)//2
        if arr[mid]==target:
            right=mid
        elif arr[0]<arr[mid]:
            if arr[0]<=target<arr[mid]:
                right=mid-1
            else:
                left=mid+1
        elif arr[0]>arr[mid]:
            if arr[mid]<target<=arr[n-1]:
                left=mid+1
            else:
                right=mid-1
        else:
                left+=1
    return -1




def search(self, arr: List[int], target: int) -> int:
    l, r = 0, len(arr) - 1
    mid = 0
    while l <= r:
        mid = l + (r - l) // 2
        if arr[mid] == target:
            while mid > 0 and arr[mid] == arr[mid-1]:
                mid -= 1
            return mid
        if arr[r] < arr[mid]:
            if arr[l] <= target < arr[mid]:
                r = mid - 1
            else:
                l = mid + 1
        elif arr[mid] < arr[r]:
            if arr[mid] < target <= arr[r]:
                l = mid + 1
            else:
                r = mid - 1
        else:
            r -= 1
    return -1



"""
public int search(int[] arr, int target) {
    if(arr[0]==target)return 0;
    int l=1,r=arr.length-1;
    while(l<=r){
        while(l<r&&arr[r]>target)r--;
        while(l<r&&arr[l]<target)l++;
        if(arr[l]==target&&arr[l-1]!=target)return l;
        if(arr[r]==target&&arr[r-1]!=target)return r;
        l++;r--;
    }
    return -1;
}
"""


























