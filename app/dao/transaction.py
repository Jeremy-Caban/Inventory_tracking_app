from app.config import dbconfig
import psycopg2

#Jeremy at work here :)

class TransactionDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port,
        )
        print(self.conn)

    query_dict = {
        #queries for master table-----
        #Todo:
        "get_all_transactions":'''
                                select * from transaction;
                                ''',

        "insert_transaction": '''insert into transaction(tdate, tquantity, ttotal, pid, sid, rid, uid)
                                values(now(), %s, %s, %s, %s, %s, %s) returning tid;
                            ''',
                                
        "update_transaction":'''
                            update transaction set tdate = now(), tquantity = %s, ttotal = %s, pid = %s,
                            sid = %s, rid = %s, uid = %s
                            where tid = %s;
                            ''',
        "delete_transaction":'''
                            delete from transaction where tid = %s;
                            ''',
        #query needed for jsonify
        "get_transaction_date":'''
                            select tdate from transaction where tid = %s;
                            ''',
        
        #queries for incoming-----
        "get_all_incoming":'''
                            select * from incomingt natural inner join transaction where incid = %s;
                            ''',
        "get_incoming_by_id":'''
                            select * from incomingt natural inner join transaction where incid = %s;
                            ''',
        "get_tid_from_incoming":'''
                            select tid from incomingt where incid = %s;
                            ''',
        "insert_incoming":'''
                            insert into incomingt(wid, tid)
                            values (%s, %s) returning incid;
                            ''',
        "update_incoming":'''
                            update incomingt set <write new vals here> where incid = %s;
                            ''',
        "delete_incoming":'''
                            delete from incomingt where incid = %s;
                            ''',
        "get_least_cost":'''
                            select tdate, sum(ttotal)
                            from warehouse natural inner join incomingt
                                natural inner join transaction
                            where wid = %s
                            group by tdate
                            order by sum(ttotal)
                            limit %s
                            ''',
        #queries for outgoing-----
        "get_all_outgoing":'''
                            select * from outgoingt;
                            ''',
        "get_outgoing_by_id":'''
                            select * from outgoingt natural inner join where outid = %s;
                            ''',
        "insert_outgoing":'''
                            insert into outgoingt(obuyer, wid, tid)
                            values (%s, %s, %s) returning outid;
                            ''',
        "update_outgoing":'''
                            update outgoingt set obuyer = %s, wid = %s, tid = %s;
                            ''',
        "delete_outgoing":'''
                            delete from outgoingt where outid = %s;
                            ''',
        #queries for exchange-----
        "get_all_exchange":'''
                            select * from transfert;
                            ''',
        "get_exchange_by_id":'''
                            select * from transfert where tranid = %s;
                            ''',
        "insert_exchange":'''
                            insert into transfert(attributes here)
                            values (%s, %s, %s, %s) returning tranid;
                            ''',
        "update_exchange":'''
                            update transfert set <write new vals here> where tranid = %s;
                            ''',
        "delete_exchange":'''
                            delete from transfert where tranid = %s;
                            '''
        
    }


    #----------------------dao for master----------------------
    def get_all_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_all_transactions"])
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def insert_transaction(self, tquantity, ttotal, pid, sid, rid, uid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["insert_transaction"], (tquantity, ttotal, pid, sid, rid, uid))
        tid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return tid

    def update_transaction(self, tquantity, ttotal, pid, sid, rid, uid, tid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["update_transaction"], (tquantity, ttotal, pid, sid, rid, uid, tid))
        self.conn.commit()
        cursor.close()
        return tid
    
    #needed for jsonify
    def get_transaction_date(self, tid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_transaction_date"], (tid,))
        tdate = cursor.fetchone()
        cursor.close()
        return tdate
    def delete_transaction(self, tid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["delete_transaction"], (tid,))
        self.conn.commit()
        cursor.close()
        return tid
    #----------------------dao for incoming----------------------
    def get_all_incoming(self):
        cursor = self.conn.cursor()
        query = "select * from incomingt natural inner join transaction;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_incoming_by_id(self, incid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_incoming_by_id"], (incid,))
        result = [row for row in cursor]
        cursor.close()
        return result
    def get_tid_from_incoming(self, incid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_tid_from_incoming"], (incid,))
        tid = cursor.fetchone()[0]
        cursor.close()
        return tid

    def insert_incoming(self, wid, tid): #modify attributes
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["insert_incoming"], (wid, tid))
        incid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return incid
    
    def update_incoming(self, wid, incid):
        cursor = self.conn.cursor()
        query = "update incomingt set wid= %s where incid = %s;"
        cursor.execute(query, (wid, incid))
        self.conn.commit()
        cursor.close()
        return incid
       
    def get_warehouse_least_cost(self, wid, amount):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_least_cost"], (wid, amount))
        result = [row for row in cursor]
        cursor.close()
        return result

    #for debugging, will be unused
    def delete_incoming(self, incid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["delete_incoming"], (incid,))
        self.conn.commit()
        cursor.close()
        return incid
    
    #----------------------dao for outgoing----------------------
    def get_all_outgoing(self):
        cursor = self.conn.cursor()
        query = "select * from outgoingt natural inner join transaction;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_outgoing_by_id(self, outid):
        cursor = self.conn.cursor()
        query = "select * from outgoingt natural inner join transaction where outid = %s;"
        cursor.execute(query, (outid,))
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_tid_from_outgoing(self, outid):
        cursor = self.conn.cursor()
        query = "select tid from outgoingt where outid = %s;"
        cursor.execute(query, (outid,))
        tid = cursor.fetchone()[0]
        cursor.close()
        return tid

    def insert_outgoing(self, obuyer, wid, tid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["insert_outgoing"], (obuyer,wid, tid))
        outid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return outid
    
    #TODO(xavier)
    def update_outgoing(self, outid, obuyer, wid):
        cursor = self.conn.cursor()
        query = "update outgoingt set obuyer = %s, wid= %s where outid = %s;"
        cursor.execute(query, (obuyer, wid, outid))
        self.conn.commit()
        cursor.close()
        return outid

    #for debugging, will be unused
    def delete_outgoing(self, tid):
        return

    #----------------------dao for exchange----------------------
    def get_all_exchange(self):
        cursor = self.conn.cursor()
        query = "select * from transfert natural inner join transaction;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_exchange_by_id(self, tranid):
        cursor = self.conn.cursor()
        query = "select * from transfert natural inner join transaction where tranid = %s;"
        cursor.execute(query, (tranid,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_tid_from_exchange(self, tranid):
        cursor = self.conn.cursor()
        query = "select tid from transfert where tranid = %s;"
        cursor.execute(query, (tranid,))
        tid = cursor.fetchone()[0]
        cursor.close()
        return tid

    def insert_exchange(self, outgoing_wid, incoming_wid, tid):
        cursor = self.conn.cursor()
        query = ''' insert into transfert(outgoing_wid, incoming_wid, tid)
                            values (%s, %s, %s) returning tranid;
'''
        cursor.execute(query, (outgoing_wid,incoming_wid, tid))
        tranid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return tranid
    
    def update_exchange(self, tranid):
        return
    #for debugging, will be unused
    def delete_exchange(self, tid):
        return
    
    #-----For Master Table-----

    # def insert_to_master_table(self, tid):
    #     return
