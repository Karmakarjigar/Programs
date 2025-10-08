import sqlite3

db = sqlite3.connect("Student.db")

'''qry = "create table stud(roll_no number,name varchar(50),city varchar(50), age number);"
qry = "insert into stud values(4,'Abhay', 'surat',12)"
qry="select * from stud;"
qry = "alter table stud add column course varchar(50);"
qry = "update stud set course='BCA' where roll_no = 4"''' 
qry = "select * from stud;"

qry = "Create table empWork(
eid integer,
ename varchar(20),
ratesPerHour integer,
totalWorkingHours integer
);"

result = db.execute(qry)

for i in result:
	print(i)

db.commit()

db.close()

print("Update successfully")