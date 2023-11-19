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
    
    def validate(self, pid, sid, rid, uid, wid, tquantity):
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
        usr_is_valid = user_wid == wid
        if user_wid != wid : return False
        # validate rack belongs to warehouse
        rack_wid = rack_dao.get_rack_warehouse(rid)
        if rack_wid != wid: return False

        # validate the part belongs to rack
        rack_pid = rack_dao.get_rack_part(rid)
        if rack_pid != pid: return False
        
        # validate sid supplies part
        supid = supplier_dao.get_supply_by_sid_and_pid(sid,pid)
        if not supid: return False
        
        # validate supplier stock
        sup_stock = supplier_dao.get_supplier_supplies_stock_by_supid(supid)[0] # this returns a list
        if sup_stock < tquantity: return False

        # validate rack capacity
        rack_capacity = rack_dao.get_rack_capacity(rid)
        cap_is_valid = rack_capacity >= tquantity
        if rack_capacity < tquantity: return False
        
        # validate warehouse budget
        ware_budget = warehouse_dao.get_warehouse_budget(wid)
        total_cost = tquantity*part_dao.get_part_price(pid)
        if ware_budget < total_cost: return False
        
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
    

    #CREATE-----
    def insert_incoming(self, json):
        KEYS_LENGTH = 8 #modify to fit all needed attr
        if len(json) == KEYS_LENGTH:
            #get from json
            tdate = json.get('tdate', None)
            tquantity = json.get('tquantity', None)
            ttotal = json.get('ttotal', None)
            pid = json.get('pid', None)
            sid = json.get('sid', None)
            rid = json.get('rid', None)
            uid = json.get('uid', None)
            wid = json.get('wid', None)
            #Check every info is being sent by json
            #if tdate and tquantity and ttotal and pid and sid and rid and uid and wid:
                #validate using daos:
                # if self.validate(pid, sid, rid, uid, wid, tquantity): #check existance of all of this  
                #     # incoming_dao = TransactionDAO()
                #     # incid = incoming_dao.insert_incoming(wid, tid)
                #     # result = self.build_attributes_dict(incid) #pass all needed attr
                #     #return jsonify(insert_transaction=result), 201
                #     return jsonify(LESS_GOOO="LES GOOO")
            test = self.validate(pid, sid, rid, uid, wid, tquantity)
            return jsonify(shit=(test))
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