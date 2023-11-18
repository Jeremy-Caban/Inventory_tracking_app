from app.config import dbconfig
import psycopg2


# Leamsi working here

class UserDAO:

    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port)
        print(self.conn)

    def getAllUsers(self):
        cursor = self.conn.cursor()
        query = "select * from public.user as u;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getUserById(self, uid):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where uid = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()
        return result

    def getUserByFirstName(self, fname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where fname = %s;"
        cursor.execute(query, (fname,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getUserByLastName(self, lname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where lname = %s;"
        cursor.execute(query, (lname,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getUserByLastName(self, lname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where lname = %s;"
        cursor.execute(query, (lname,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getUserByFullName(self, fname, lname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where fname = %s and lname = %s;"
        cursor.execute(query, (fname, lname))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getUserByEmail(self, uemail):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where uemail = %s;"
        cursor.execute(query, (uemail,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getUserByPhone(self, uphone):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where uphone = %s;"
        cursor.execute(query, (uphone,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def insert(self, fname, lname, uemail=None, uphone=None):
        cursor = self.conn.cursor()
        query = '''
                insert into public.user(fname, lname, uemail, uphone) as u
                values (%s, %s, %s, %s) returning uid;
                '''
        cursor.execute(query, (fname, lname, uemail, uphone))
        uid = cursor.fetchone()[0]
        self.conn.commit()
        return uid

    def update(self, uid, fname, lname, uemail, uphone):
        cursor = self.conn.cursor()
        query = "update public.user as u set fname = %s, lname = %s, uemail = %s, uphone = %s where uid = %s;"
        cursor.execute(query, (fname, lname, uemail, uphone, uid))
        self.conn.commit()
        return uid

    def delete(self, uid):
        cursor = self.conn.cursor()
        query = "delete from public.user as u where uid = %s;"
        cursor.execute(query, (uid,))
        self.conn.commit()
        return uid
