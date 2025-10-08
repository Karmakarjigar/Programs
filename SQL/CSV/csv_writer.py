import csv

fields = ['Roll no', 'Name', 'Address', 'Phone-No']

data =[
        ['1', 'Carl', 'Bens Street', '125486-565'],
        ['2', 'Jules', 'Ap james', '125486-565'],
        ['3', 'Markes', 'Bens Street', '125486-565'],
        ['4', 'Hendry', 'Bens Street', '125486-565'],
        ['5', 'Ben', 'Bens Street', '125486-565']
    ]

file = "data.csv"
with open(file,'w',newline="") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(fields)
    csv_writer.writerows(data)
