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
        return result

    def get_warehouse_by_id(self, wid):
        cursor = self.conn.cursor()
        query = 'select * from warehouse as w where w.wid = %s;'
        cursor.execute(query, (wid,))
        result = [row for row in cursor]
        return result

    def get_warehouse_by_name(self, wname):
        cursor = self.conn.cursor()
        query = 'select * from warehouse as w where w.wname = %s;'
        cursor.execute(query, (wname,))
        result = [row for row in cursor]
        return result

    def get_warehouse_most_racks(self,amount:int):
        cursor = self.conn.cursor()
        query = """select * from (
                    select wid, count(rid) as count
                    from rack natural inner join warehouse
                    group by wid
            ) as list
                natural inner join warehouse
                order by list.count desc
                limit %s;
        """
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        return result
