import csv

file = open("cust.csv","r")
data = csv.DictReader(file)
next(data)
next(data)
for i in data:
    print(i)
    
file.close()
    