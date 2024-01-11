from app.handlers import user, rack, warehouse, parts, transaction, supplier
from app.config import dbconfig
import psycopg2

dbconfig.host = "localhost"
dbconfig.dbname = "testdb"
dbconfig.user = "postgres"
dbconfig.password = "postgres"
dbconfig.port = "5432"


def reset_db():
    # List of tables to truncate
    tables_to_truncate = [
        'works', 'supplies', 'inside', 'incomingt', 'outgoingt',
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

w = warehouse.WarehouseHandler()
u = user.UserHandler()
r = rack.RackHandler()
s = supplier.SupplierHandler()
p = parts.PartHandler()
t = transaction.TransactionHandler()


w.insert_warehouse({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@lol", "wphone":"787-0DB-TEST", "budget":500})
w.insert_warehouse({"wname":"big balling warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":10000})
w.insert_warehouse({"wname":"small balling warehouse", "wcity":"San Juan", "wemail":"db@yolo", "wphone":"787-0DB-TEST", "budget":1})
w.insert_warehouse({"wname":"bobs warehouse", "wcity":"Mayaguez", "wemail":"db@jaja", "wphone":"787-0DB-TEST", "budget":100})