import sqlite3

db = sqlite3.connect('emp.db')

qry = '''select * from Emp'''
cr = db.cursor()
result = cr.execute(qry)
for i in cr.fetchall():
    print(i)

db.commit()
db.close()

print("table printing")