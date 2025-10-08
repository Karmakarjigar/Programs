import csv

path = 'SQL\customers-100.csv'
file = open(path,'r')

fileRead = csv.DictReader(file)

for i in fileRead:
    print(i)
    break

fileRead = csv.reader(file)

for i in fileRead:
    print(i)
    break
