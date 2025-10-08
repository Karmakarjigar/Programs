import sqlite3

db = sqlite3.connect("cust.db")

"""qry = 
CREATE TABLE cust(
    cust_index INTEGER,
    customer_id INTEGER,
    first_name TEXT,
    last_name TEXT
)
"""
'''qry = """insert into cust values(4,2897,'Mary','jane');"""'''
qry = "select * from cust"
result = db.execute(qry)
for i in result:
    print(i)

db.commit()
db.close()

