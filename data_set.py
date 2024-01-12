from app.handlers import user, rack, warehouse, parts, transaction, supplier
from app.config import dbconfig
import psycopg2
from app import app

#Seba Local DB Credentials
# dbconfig.host = "localhost"
# dbconfig.dbname = "testdb"
# dbconfig.user = "postgres"
# dbconfig.password = "postgres"
# dbconfig.port = "5432"

#Jeremy Local DB Credentials
dbconfig.user = 'postgres'
dbconfig.password = 'DBLosCangri587'
dbconfig.dbname = 'postgres'
dbconfig.host = 'localhost'
dbconfig.port = 5432

a = app.test_client()

def reset_db():
    # List of tables to truncate
    tables_to_truncate = [
        'supplies', 'incomingt', 'outgoingt',
        'transaction', '"user"', 'supplier', 'rack', 'parts',
        'transfert', 'warehouse'
    ]
    try:
        with psycopg2.connect(user=dbconfig.user, password=dbconfig.password, host=dbconfig.host, dbname=dbconfig.dbname, port=dbconfig.port) as conn:
            with conn.cursor() as cursor:
                for table in tables_to_truncate:
                    query = f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"
                    cursor.execute(query)
                    print(f"Truncated table {table}")
        return True
    except Exception as e:
        print(e)
        return False   
    
reset_db()
p = '/los-cangri/part'
w = '/los-cangri/warehouse'
u = '/los-cangri/user'
r = '/los-cangri/rack'
s = '/los-cangri/supplier'
i = '/los-cangri/incoming'
o = '/los-cangri/outgoing'
e = '/los-cangri/exchange'



#Part Creation--------------------------------------------------------
# pypes{ Plastic: 3, Wood: 4, Steel: 1, PVC: 1}
a.post(p, json = {"pprice":100, "ptype":"Plastic", "pname":"Table"}) #1
a.post(p, {"pprice":75, "ptype":"Steel", "pname":"Pipe"}) #2
a.post(p, {"pprice":10, "ptype":"Wood", "pname":"Plank"}) #3
a.post(p, {"pprice":250, "ptype":"Plastic", "pname":"Cupboard"}) #4
a.post(p, {"pprice":500, "ptype":"Wood", "pname":"Door"}) #5
a.post(p, {"pprice":775, "ptype":"Wood", "pname":"Sculpture"}) #6
a.post(p, {"pprice":35, "ptype":"Plastic", "pname":"Bottle"}) #7
a.post(p, {"pprice":385, "ptype":"PVC", "pname":"Kiddie Pool"}) #8
a.post(p, {"pprice":75, "ptype":"Wood", "pname":"Table"}) #9
#Supplier Creation------------------------------------------------------
#Supp 1
a.post(s, {"sname":"Berrios Imports", "scity":"Moca", "sphone":"787-0DB-TEST", "semail":"test@gmail.com"}) 
#Supp 2
a.post(s, {"sname":"Sams Club", "scity":"Trujillo", "sphone":"787-1DB-TEST", "semail":"test@hotmail.com"})
#Supp 3
a.post(s, {"sname":"Sears", "scity":"Aguada", "sphone":"787-2DB-TEST", "semail":"test@icloud.com"})
#Supp 4
a.post(s, {"sname":"Walgreens", "scity":"San Juan", "sphone":"787-3DB-TEST", "semail":"test@business.com"})

#Supplies Creation (Each Supplier will supply 3 parts)--------------------
#Supplier 1
a.post(s+f"/{1}", {"pid":"1", "stock":100})
a.post(s+f"/{1}", {"pid":"2", "stock":100})
a.post(s+f"/{1}", {"pid":"3", "stock":100})

#Supplier 2
a.post(s+f"/{2}", {"pid":"3", "stock":50})
a.post(s+f"/{2}", {"pid":"5", "stock":50})
a.post(s+f"/{2}", {"pid":"6", "stock":50})

#Supplier 3
a.post(s+f"/{3}", {"pid":"7", "stock":40})
a.post(s+f"/{3}", {"pid":"4", "stock":40})
a.post(s+f"/{3}", {"pid":"8", "stock":40})

#Supplier 4
a.post(s+f"/{4}", {"pid":"4", "stock":30})
a.post(s+f"/{4}", {"pid":"3", "stock":30})
a.post(s+f"/{4}", {"pid":"9", "stock":30})

#Warehouse Creation-------------------------------------------------------
#cities: Aguada: 4, San Juan: 1, Mayaguez: 3, Caguas: 1, Moca: 1, Fajardo: 1
a.post(w,  {"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@lol", "wphone":"787-1DB-TEST", "budget":500}) #1
a.post(w,  {"wname":"big balling warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-2DB-TEST", "budget":10000}) #2
a.post(w,  {"wname":"small balling warehouse", "wcity":"San Juan", "wemail":"db@yolo", "wphone":"787-3DB-TEST", "budget":500}) #3
a.post(w,  {"wname":"bobs warehouse", "wcity":"Mayaguez", "wemail":"db@gmail", "wphone":"787-4DB-TEST", "budget":100}) #4
a.post(w,  {"wname":"Database Warehouse", "wcity":"Caguas", "wemail":"db@hotmail", "wphone":"787-5DB-TEST", "budget":500}) #5
a.post(w,  {"wname":"Jeremy Warehouse", "wcity":"Aguada", "wemail":"db@Jeremy", "wphone":"787-6DB-TEST", "budget":10000}) #6
a.post(w,  {"wname":"Sebastian warehouse", "wcity":"Moca", "wemail":"db@Sebastian", "wphone":"787-7DB-TEST", "budget":500}) #7
a.post(w,  {"wname":"Xavier warehouse", "wcity":"Mayaguez", "wemail":"db@Xavier", "wphone":"787-8DB-TEST", "budget":100}) #8
a.post(w,  {"wname":"Leamsi Warehouse", "wcity":"Fajardo", "wemail":"db@Leamsi", "wphone":"787-9DB-TEST", "budget":500}) #9
a.post(w,  {"wname":"Los Cangri Warehouse", "wcity":"Mayaguez", "wemail":"db@Cangri", "wphone":"787-0DB-TEST", "budget":300}) #10
a.post(w,  {"wname":"Phase 3 Warehouse", "wcity":"Aguada", "wemail":"db@Phase3", "wphone":"787-0DB-TEST", "budget":1}) #11

#User Creation---------------------------------------------------------------------------------
first_names = ["Ethan", "Ava", "Lucas", "Mia", "Oliver", "Sophia", "Noah", "Isabella", "Liam", "Olivia", "Jackson", "Emma", "Aiden", "Harper", "Caleb", "Abigail", "Mason", "Emily", "Logan", "Ella", "Benjamin", "Scarlett"]

last_names = ["Johnson", "Smith", "Williams", "Brown", "Jones", "Garcia", "Davis", "Rodriguez", "Martinez", "Hernandez", "Jackson", "Taylor", "Anderson", "Thomas", "White", "Harris", "Martin", "Thompson", "Robinson", "Clark", "Lewis", "Walker"]
wid = 1
for i in range(22):
    a.post(u, {"fname": first_names[i],"lname": last_names[i],"uemail": "db@test","uphone":"787-0DB-TEST","wid": wid})
    if (i+1) % 2 == 0:
        wid += 1
    
    
#Rack Creation---------------------------------------------------------------------------------
r.insert_rack({"capacity":100, "wid":7, "quantity":12, "pid":52})

#Transaction Creation---------------------------------------------------------------------------------

#incoming

#outgoing

#exchange