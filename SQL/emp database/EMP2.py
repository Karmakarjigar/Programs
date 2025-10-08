import sqlite3

db = sqlite3.connect("emp.db")

'''qry = "create table depart(d_id number,depart_name varchar(50))"'''
'''qry = "insert into depart values(201,'IT');"'''
qry = "select * from depart;"
cr = db.cursor()
result = cr.execute(qry)
for i in result:
    print(i)
db.commit()
db.close()

print("Table created")
