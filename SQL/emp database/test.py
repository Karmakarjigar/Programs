n = 7
c = 0
for i in range(0, n + 1):
    c += 0.5
c *= n

for i in range(n,0,-1):
    for j in range(1, i + 1):
        print(c, end=" ")
        c -= 1
    print()