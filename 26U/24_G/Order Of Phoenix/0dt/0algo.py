




#get keyboard
l1 = "qwertyuiop"
l2 = "asdfghjkl"
l3 = "zxcvbnm"
key = [l1, l2, l3]
keyboard = []

for l in key:
    line = [i for i in l]
    line += [i.upper() for i in line]
    keyboard.append(line)

print(keyboard)







