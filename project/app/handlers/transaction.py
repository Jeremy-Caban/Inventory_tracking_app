from flask import jsonify
from app.dao.transaction import TransactionDAO
from app.dao.rack import RackDAO
from app.dao.warehouse import WarehouseDAO
from app.dao.user import UserDAO
from app.dao.parts import PartsDAO
from app.dao.supplier import SupplierDAO
class TransactionHandler:
    #KEYS
    incoming_keys = ['tdate','tquantity','ttotal','pid','sid', 'rid','uid','wid']
    outgoing_keys = ['tdate','tquantity','ttotal','pid','sid', 'rid','uid','obuyer','wid']
    exchange_keys = []
    transaction_keys = ['tdate','tquantity','ttotal','pid','sid', 'rid','uid']
    #DAOS
    # part_dao = PartsDAO()
    # supplier_dao = SupplierDAO()
    # rack_dao = RackDAO()
    # user_dao = UserDAO()
    # warehouse_dao = WarehouseDAO()
    #-----Helper methods-----
    def build_attributes_dict(self, attr_array, ttype):
        keys = []
        if ttype == "incoming":
            keys = self.incoming_keys
        elif ttype ==  "outgoing":
            keys = self.outgoing_keys
        elif ttype == "exchange":
            keys = self.exchange_keys
        return dict(zip(keys, attr_array))

    #Only really used for incoming transactions as per spec
    def build_least_cost_dict(self, rows):
        keys = ['date','amount']
        return dict(zip(keys, rows))
    
    def validate(self, pid, sid, rid, uid, wid, tquantity, ttotal):
        #validate existance of these
        #DAOS
        part_dao = PartsDAO()
        supplier_dao = SupplierDAO()
        rack_dao = RackDAO()
        user_dao = UserDAO()
        warehouse_dao = WarehouseDAO()

        part_row = part_dao.getPartById(pid)
        supplier_row = supplier_dao.get_supplier_by_ID(sid)
        rack_row = rack_dao.get_rack_by_id(rid)
        user_row = user_dao.getUserById(uid)
        warehouse_row = warehouse_dao.get_warehouse_by_id(wid)
        if not (part_row and supplier_row and rack_row and user_row and warehouse_row): return False
        
        # validate user belongs to warehouse
        user_wid = user_dao.getUserWarehouse(uid)
        #print(user_wid)
        #print("User Belongs to Warehouse: "+user_wid != wid)
        if user_wid[0] != wid : return False

        # validate rack belongs to warehouse
        rack_wid = rack_dao.get_rack_warehouse(rid)
        #print("Rack belongs to warehouse: "+rack_wid != wid)
        #print(rack_wid)
        if rack_wid[0] != wid: return False

        # validate the part belongs to rack

        rack_pid = rack_dao.get_rack_part(rid)
        #print("Part belongs to rack: "+rack_pid != pid)
        if rack_pid[0] != pid: return False
        
        # validate sid supplies part
        supid = supplier_dao.get_supply_by_sid_and_pid(sid,pid)
        #print("Supplier provide part: "+ supid)
        if not supid: return False
        
        # validate supplier stock
        sup_stock = supplier_dao.get_supplier_supplies_stock_by_supid(supid)
        #print("Valid Stock: "+sup_stock < tquantity)
        if sup_stock < tquantity: return False

        # validate rack capacity
        rack_capacity = rack_dao.get_rack_capacity(rid)
        curr_rack_quantity = rack_dao.get_rack_quantity(rid)
        free_space = rack_capacity-curr_rack_quantity #verify if this is the correct assumption to make
        #print("Free space: "+free_space < tquantity)
        if free_space < tquantity: return False
        
        # validate warehouse budget
        ware_budget = warehouse_dao.get_warehouse_budget(wid)
        total_cost = tquantity*part_dao.get_part_price(pid)
        
        if ware_budget < total_cost: return False
        if total_cost != ttotal: return False
        
        return True
        
    #----------------------CRUD for incoming----------------------
    #READ-----
    def get_all_incoming(self):
        dao = TransactionDAO()
        all_incoming = dao.get_all_incoming()
        result = []
        for row in all_incoming:
            result.append(self.build_attributes_dict(row))
        return jsonify(incoming=result)
    
    def get_incoming_by_id(self, incid):
        dao = TransactionDAO()
        row = dao.get_incoming_by_id(incid)
        if not row:
            return jsonify(Error = "Incoming transaction not found"), 404
        else:
            incoming = self.build_attributes_dict(row[0]) #note: dao.get_incoming_by_id returns a list of rows
            return jsonify(Incoming = incoming)
    

    def get_warehouse_least_cost(self, wid, json, amount=3):
        dao = TransactionDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User has no access to warehouse'), 403
        transaction_list = dao.get_warehouse_least_cost(wid, amount)
        result = [self.build_least_cost_dict(row) for row in transaction_list]
        return jsonify(Dates=result)

    #CREATE-----
    def insert_incoming(self, json):
        KEYS_LENGTH = 7 #modify to fit all needed attr
        if len(json) == KEYS_LENGTH:
            #get from json
            #tdate = json.get('tdate', None)
            tquantity = json.get('tquantity', None)
            ttotal = json.get('ttotal', None)
            pid = json.get('pid', None)
            sid = json.get('sid', None)
            rid = json.get('rid', None)
            uid = json.get('uid', None)
            wid = json.get('wid', None)
            #Check every info is being sent by json
            #tdate <-- don't validate for this since it'll be created in the dao via the now() method
            if tquantity and ttotal and pid and sid and rid and uid and wid:
                #validate using daos:
                if self.validate(pid, sid, rid, uid, wid, tquantity, ttotal): #check if valid data is sent  
                    #daos
                    transaction_dao = incoming_dao = TransactionDAO()
                    warehouse_dao = WarehouseDAO()
                    rack_dao = RackDAO()
                    supplier_dao = SupplierDAO()
                    #create entry in master transactions
                    tid = transaction_dao.insert_transaction(tquantity, ttotal, pid, sid, rid, uid)
                    #create entry in incoming transactions
                    incid = incoming_dao.insert_incoming(wid, tid)
                    print(incid) #random print
                    #prep results
                    tdate = incoming_dao.get_transaction_date(tid)
                    attr_array = [tdate, tquantity, ttotal, pid, sid, rid, uid, wid]
                    
                    # #-----Updates-----
                    # #update warehouse:
                    warehouse_budget = warehouse_dao.get_warehouse_budget(wid)
                    new_budget = warehouse_budget - ttotal

                    wid = warehouse_dao.set_warehouse_budget(wid, new_budget)
                    # #update rack:
                    
                    new_quantity = rack_dao.get_rack_quantity(rid) + tquantity
                    # print("New_quantity: "+new_quantity)
                    rid = rack_dao.set_rack_quantity(rid, new_quantity)
                    # #update supplies:
                    
                    new_stock = supplier_dao.get_supplier_supplies_stock_by_sid_and_pid(sid, pid) - tquantity
                    # print("New_stock: "+new_stock)
                    sid,pid = supplier_dao.edit_supplies_stock_by_sid_and_pid(sid, pid, new_stock)
                    # #-----End Updates-----

                    #show results
                    result = self.build_attributes_dict(attr_array, self.incoming_keys)
                    return jsonify(Incoming=result)
                else:
                    return jsonify(Error="Invalid Data")
        return jsonify(Error="Unexpected/Missing attributes in request.")
    

    #UPDATE-----
    def update_incoming(self, tid, json):
        return
    

    #DELETE (ONLY FOR DEBUGGING)
    def delete_incoming(self):
        return
    
    #----------------------CRUD for outgoing----------------------

    #READ-----
    def get_all_outgoing(self):
        dao = TransactionDAO()
        all_outgoing = dao.get_all_outgoing()
        result = []
        for row in all_outgoing:
            result.append(self.build_attributes_dict(row))
        return jsonify(Outgoing=result)
    
    def get_outgoing_by_id(self, outid):
        dao = TransactionDAO()
        row = dao.get_outgoing_by_id(outid)
        if not row:
            return jsonify(Error = "Outgoing transaction not found"), 404
        else:
            outgoing = self.build_attributes_dict(row[0])
            return jsonify(Outgoing = outgoing)
    

    #CREATE-----
    def insert_outgoing(self, json):
        return
    

    #UPDATE-----
    def update_outgoing(self, tid, json):
        return
    

    #DELETE (ONLY FOR DEBUGGING)
    def delete_outgoing(self):
        return
    
    #----------------------CRUD for exchange----------------------
    
    #READ-----
    def get_all_exchange(self):
        dao = TransactionDAO()
        all_exchange = dao.get_all_exchange()
        result = []
        for row in all_exchange:
            result.append(self.build_attributes_dict(row))
        return jsonify(exchange=result)
    
    def get_exchange_by_id(self, tranid):
        dao = TransactionDAO()
        row = dao.get_exchange_by_id(tranid)
        if not row:
            return jsonify(Error = "Exchange transaction not found"), 404
        else:
            exchange = self.build_attributes_dict(row[0])
            return jsonify(Outgoing = exchange)
    

    #CREATE-----
    def insert_exchange(self, json):
        return
    

    #UPDATE-----
    def update_exchange(self, tid, json):
        return
    

    #DELETE (ONLY FOR DEBUGGING)
    def delete_exchange(self):
        return
