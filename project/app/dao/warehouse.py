from app.config import dbconfig
import psycopg2

#TODO(xavier)
class WarehouseDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port)
        print(self.conn)

    def get_all_warehouses(self):
        cursor = self.conn.cursor()
        query = "select * from warehouse;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_by_id(self, wid):
        cursor = self.conn.cursor()
        query = 'select * from warehouse as w where w.wid = %s;'
        cursor.execute(query, (wid,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_by_name(self, wname):
        cursor = self.conn.cursor()
        query = 'select * from warehouse as w where w.wname = %s;'
        cursor.execute(query, (wname,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_most_incoming(self,amount):
        cursor = self.conn.cursor()
        query = '''
        select wid, count(incid)
        from warehouse natural inner join incomingt
        group by wid
        order by count(incid) desc
        limit %s;
        '''
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_most_racks(self,amount:int):
        cursor = self.conn.cursor()
        query = '''
        select wid, count(rid)
        from rack natural inner join warehouse
        group by wid
        order by count(rid) desc
        limit %s;
        '''
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def insert(self, wname, wcity, wemail=None, wphone=None, budget=0):
        cursor= self.conn.cursor()
        query = '''
           insert into warehouse(wname, wcity, wemail, wphone, budget)
           values (%s, %s, %s, %s, %s) returning wid;
        '''
        cursor.execute(query, (wname, wcity, wemail, wphone, budget))
        wid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return wid

    def update(self, wid, wname, wcity, wemail, wphone, budget):
        cursor = self.conn.cursor()
        query = '''
            update warehouse set wname = %s, wcity = %s, wemail = %s,
                wphone = %s, budget = %s
            where wid = %s;
        '''
        cursor.execute(query, (wname, wcity, wemail, wphone, budget, wid))
        self.conn.commit()
        cursor.close()
        return wid

    def delete(self, wid):
        cursor = self.conn.cursor()
        query = '''
            delete from warehouse where wid = %s;
        '''
        cursor.execute(query, (wid,))
        self.conn.commit()
        cursor.close()
        return wid

    #queries needed for validation
    def get_warehouse_budget(self, wid):
        cursor = self.conn.cursor()
        query = '''
            select budget from warehouse as w where w.wid = %s;
        '''
        cursor.execute(query, (wid,))
        budget = cursor.fetchone()[0]
        cursor.close()
        return budget
    
    def set_warehouse_budget(self, wid, new_budget):
        cursor = self.conn.cursor()
        query = '''
            update warehouse set budget = %s where wid = %s;
        '''
        cursor.execute(query, (new_budget, wid))
        self.conn.commit()
        cursor.close()
        return wid
