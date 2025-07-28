"""
111.360. Sort Transformed Array   
有序转化数组

"""

return sorted([a*x**2+b*x+c for x in nums])


def sortTransformedArray(self, nums, a, b, c):
        """
        :type nums: List[int]
        :type a: int
        :type b: int
        :type c: int
        :rtype: List[int]
        """
        # 计算ax2 + bx + c
        def getValue(v):
            return a * v * v + b * v + c
        # 如果a == 0，则结果是线性的，根据b的值确定正序or逆序
        if a == 0:
            if b >= 0:
                # 正序输出
                return map(getValue, nums)
            else:
                # 逆序输出
                return map(getValue, reversed(nums))
        else:
            # 计算对称轴x坐标
            symmetry_coordinates = -(b/(2.0*a))
            l = len(nums)
            out = range(l)
            left, right = 0, l-1
            # a>0时，按照距离逆序输出，否则按照距离正序输出
            if a > 0:
                index = right
            else:
                index = left
            while left <= right:
                # 获取到对称轴的距离
                distance_left = abs(nums[left] - symmetry_coordinates)
                distance_right = abs(nums[right] - symmetry_coordinates)
                if distance_left > distance_right:
                    out[index] = getValue(nums[left])
                    left += 1
                else:
                    out[index] = getValue(nums[right])
                    right -= 1
                if a > 0:
                    index -= 1
                else:
                    index += 1  
            return out


