from app.config import dbconfig  
import psycopg2

class PartsDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port)
        
        print(self.conn)

    def getAllParts(self):
        cursor = self.conn.cursor()
        query = "select * from parts;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result    