from app.config import dbconfig
import psycopg2

#Jeremy at work here :)

class SupplierDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port,
        )
        print(self.conn)

    #-----CRUD operations start here-----

    #Create
    def insert(self, sname, scity, sphone=None, semail=None):
        cursor = self.conn.cursor()
        query = '''
                insert into supplier(sname, scity, sphone, semail)
                values (%s, %s, %s, %s) returning sid;
                '''
        cursor.execute(query, (sname, scity, sphone, semail))
        sid = cursor.fetchone()[0]
        self.conn.commit()
        return sid
    
    #Read---------------------
    def get_all_suppliers(self):
        cursor = self.conn.cursor()
        query = "select * from supplier;"
        cursor.execute(query)
        result = [row for row in cursor]
        return result

    def get_supplier_by_ID(self, sid):
        cursor = self.conn.cursor()
        query = "select * from supplier as s where s.sid = %s;"
        cursor.execute(query, (sid,))
        result = [row for row in cursor]
        return result

    #unused
    # def get_supplier_by_name(self, sname):
    #     cursor = self.conn.cursor()
    #     query = "select * from supplier as s where s.sname = %s;"
    #     cursor.execute(query, (sname,))
    #     result = [row for row in cursor]
    #     return result
    
    # def get_supplier_by_city(self, scity):
    #     cursor = self.conn.cursor()
    #     query = "select * from supplier as s where s.scity = %s;"
    #     cursor.execute(query, (scity,))
    #     result = [row for row in cursor]
    #     return result
    #-------------------------

    #Update
    def update(self, sid, scity, sname, sphone, semail):
        cursor = self.conn.cursor()
        query = '''
                    update supplier set scity = %s, sname = %s, sphone = %s, semail = %s
                    where sid = %s;
                '''
        cursor.execute(query, (scity, sname, sphone, semail, sid))
        self.conn.commit()
        return sid
    
    #Delete
    def delete(self, sid):
        cursor = self.conn.cursor()
        query = "delete from supplier where sid = %s;"
        cursor.execute(query, (sid,))
        self.conn.commit()
        return sid

    #-----CRUD operations end here-----

    #-----Additional Query Operations after here-----