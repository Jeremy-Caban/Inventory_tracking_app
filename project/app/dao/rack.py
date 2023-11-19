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

    def insert(self, capacity, quantity, pid, wid):
        cursor= self.conn.cursor()
        query = '''
           insert into rack(capacity, wid, quantity, pid)
           values (%s, %s, %s, %s) returning rid;
        '''
        cursor.execute(query, (capacity, wid, quantity, pid))
        rid = cursor.fetchone()[0]
        self.conn.commit()
        return rid

    def update(self, rid, capacity, quantity, pid, wid):
        cursor = self.conn.cursor()
        query = '''
            update rack set capacity = %s, wid = %s, quantity = %s, pid = %s
            where rid = %s;
        '''
        cursor.execute(query, (capacity, wid, quantity, pid, rid))
        self.conn.commit()
        return rid

    def delete(self, rid):
        cursor = self.conn.cursor()
        query = '''
            delete from rack where rid = %s;
        '''
        cursor.execute(query, (rid,))
        self.conn.commit()
        return rid

    def get_parts_in_rack(self, rid):
        cursor = self.conn.cursor()
        query = '''
            select * from parts natural inner join rack as r where r.rid = %s;
        '''
        cursor.execute(query, (rid,))
        result = [row for row in cursor]
        return result


