arr = [('gaurav',2),('Ardak',7),('Chandrakant',5),('raj',9)]
result = []
finale = []
arr2 = []
finalresult = []
for (x,y) in arr:
    result.append(y)
finale.append(max(result))
for n in arr:
    if n[1] == finale:
        finalresult.append((n[0],n[1]))
print(finalresult)

