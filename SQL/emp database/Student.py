import sqlite3
db = sqlite3.connect("emp.db")

'''qry = "create table Student(roll_no integer, name text, City text, age integer);"
qry = "insert into Student values(4,'Jash','Navsari',21);"
qry = "select * from Student;"
qry = "alter table Student add Course text;"
qry = "update Student set Course = 'B.Com' where roll_no = 2;"
qry = "Select * from Student;"'''
qry = "select * from Student where city = 'Navsari' and Course = 'BCA' "

result = db.execute(qry)

for i in result:
	print(i)
'''db.execute(qry)'''

db.commit()
db.close()