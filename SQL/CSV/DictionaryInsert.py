import csv

fields = ['Roll no', 'Name', 'Address', 'Phone-No']

data =[
        {'Roll no' : '1','Name': 'Carl', 'Address':'Bens Street', 'Phone-No':'125486-565'},
        {'Roll no' : '2','Name': 'Jules', 'Address':'Bens Street', 'Phone-No':'125486-565'},
        {'Roll no' : '3','Name': 'Markes', 'Address':'Bens Street', 'Phone-No':'125486-565'},
        {'Roll no' : '4','Name': 'Hendry', 'Address':'Bens Street', 'Phone-No':'125486-565'},
        {'Roll no' : '5','Name': 'Ben', 'Address':'Bens Street', 'Phone-No':'125486-565'}
    ]

file = "Data1.csv"

with open(file,"w",newline="") as f:
    csv_writer = csv.DictWriter(f,fieldnames = fields)
    csv_writer.writeheader()
    csv_writer.writerows(data)
    
    
    
    
data.append({'Roll no' : '6','Name': 'James', 'Address':'Bens Street', 'Phone-No':'125486-565'})