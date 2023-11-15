from app.config import dbconfig
import psycopg2

#TODO(xavier)
class RackDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port)
        print(self.conn)

    def get_all_racks(self):
        cursor = self.conn.cursor()
        query = "select * from rack;"
        cursor.execute(query)
        result = [row for row in cursor]
        return result

    def get_rack_by_id(self, rid):
        cursor = self.conn.cursor()
        query = 'select * from rack as r where r.rid = %s;'
        cursor.execute(query, (rid,))
        result = [row for row in cursor]
        return result

    def insert(self, capacity, wid):
        cursor= self.conn.cursor()
        query = '''
           insert into rack(capacity, wid)
           values (%s, %s) returning rid;
        '''
        cursor.execute(query, (capacity, wid))
        rid = cursor.fetchone()[0]
        self.conn.commit()
        return rid

    def update(self, rid, capacity, wid):
        cursor = self.conn.cursor()
        query = '''
            update rack set capacity = %s, wid = %s
            where rid = %s;
        '''
        cursor.execute(query, (capacity, wid, rid))
        self.conn.commit()
        return rid

    def delete(self, rid):
        cursor = self.conn.cursor()
        query = '''
            delete from warehouse where rid = %s;
        '''
        cursor.execute(query, (rid,))
        self.conn.commit()
        return rid
