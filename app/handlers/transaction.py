from flask import jsonify
from app.dao.transaction import TransactionDAO
from app.dao.rack import RackDAO
from app.dao.warehouse import WarehouseDAO
from app.dao.user import UserDAO
from app.dao.parts import PartsDAO
from app.dao.supplier import SupplierDAO

class TransactionHandler:
    #KEYS
    incoming_keys = ['tid', 'icid','tdate','tquantity','ttotal','pid','sid', 'rid','uid','wid']
    outgoing_keys = ['tid', 'outid','obuyer', 'wid', 'tdate','tquantity','ttotal','pid','sid', 'rid','uid']
    exchange_keys = ['tid', 'tranid','outgoing_wid', 'incoming_wid', 'tdate', 'tquantity','ttotal','pid','sid', 'rid','uid']
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
    
    def validate_outgoing(self, pid, sid, rid, uid, wid, tquantity):
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

        if not part_row:
            raise ValueError('Provided PID invalid')
        if not supplier_row:
            raise ValueError('Provided SID invalid')
        if not rack_row:
            raise ValueError('Provided RID invalid')
        if not user_row:
            raise ValueError('Provided UID invalid')
        if not warehouse_row:
            raise ValueError('Provided WID invalid')

        supid = supplier_dao.get_supply_by_sid_and_pid(sid,pid)
        if not supid:
            raise ValueError('Provided supplier does not provide this part')

        #validate user belongs to warehouse
        user_wid = user_dao.getUserWarehouse(uid)[0]
        if user_wid != wid:
            raise ValueError('User does work for given warehouse')

        rack_pid = rack_dao.get_rack_part(rid)[0]
        if rack_pid != pid:
           raise ValueError('Rack does not hold provided part')
        return True


    def validate_incoming(self, pid, sid, rid, uid, wid, tquantity, ttotal):
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
        if user_wid[0] != wid :
            print('user no access')
            return False

        # validate rack belongs to warehouse
        rack_wid = rack_dao.get_rack_warehouse(rid)
        #print("Rack belongs to warehouse: "+rack_wid != wid)
        #print(rack_wid)
        if rack_wid[0] != wid:
            print('rackwid')
            return False

        # validate the part belongs to rack

        rack_pid = rack_dao.get_rack_part(rid)
        #print("Part belongs to rack: "+rack_pid != pid)
        if rack_pid[0] != pid:
            print('rackpid')
            return False
        
        # validate sid supplies part
        supid = supplier_dao.get_supply_by_sid_and_pid(sid,pid)
        #print("Supplier provide part: "+ supid)
        if not supid:
            print('no supid')
            return False
        
        # validate supplier stock
        sup_stock = supplier_dao.get_supplier_supplies_stock_by_supid(supid)
        #print("Valid Stock: "+sup_stock < tquantity)
        if sup_stock < tquantity:
            print('no stock lol')
            return False

        # validate rack capacity
        rack_capacity = rack_dao.get_rack_capacity(rid)
        curr_rack_quantity = rack_dao.get_rack_quantity(rid)
        free_space = rack_capacity-curr_rack_quantity #verify if this is the correct assumption to make
        #print("Free space: "+free_space < tquantity)
        if free_space < tquantity:
            print('no rack space')
            return False
        
        # validate warehouse budget
        ware_budget = warehouse_dao.get_warehouse_budget(wid)
        total_cost = tquantity*part_dao.get_part_price(pid)
        
        if ware_budget < total_cost:
            print('no budget')
            return False
        if total_cost != ttotal:
            print('total cost is allot')
            return False
        
        return True
        
    #----------------------CRUD for incoming----------------------
    #READ-----
    def get_all_incoming(self):
        dao = TransactionDAO()
        all_incoming = dao.get_all_incoming()
        result = []
        for row in all_incoming:
            result.append(self.build_attributes_dict(row,"incoming"))
        return jsonify(incoming=result)
    
    def get_incoming_by_id(self, incid):
        dao = TransactionDAO()
        row = dao.get_incoming_by_id(incid)
        if not row:
            return jsonify(Error = "Incoming transaction not found"), 404
        else:
            incoming = self.build_attributes_dict(row[0], "incoming") #note: dao.get_incoming_by_id returns a list of rows
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
                if self.validate_incoming(pid, sid, rid, uid, wid, tquantity, ttotal): #check if valid data is sent  
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
                    attr_array = [tid, incid, tdate, tquantity, ttotal, pid, sid, rid, uid, wid]
                    
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
                    result = self.build_attributes_dict(attr_array, "incoming")
                    return jsonify(Incoming=result)
                else:
                    return jsonify(Error="Invalid Data")
        return jsonify(Error="Unexpected/Missing attributes in request.")
    

    #UPDATE-----
    def update_incoming(self, incid, json):
        if len(json)!=7: return jsonify(Error="Unexpected/Missing attributes in request.")
        dao = TransactionDAO()
        tquantity = json.get('tquantity', None)
        ttotal = json.get('ttotal', None)
        pid = json.get('pid', None)
        sid = json.get('sid', None)
        rid = json.get('rid', None)
        uid = json.get('uid', None)
        wid = json.get('wid', None)
        if incid and tquantity and ttotal and pid and sid and rid and uid and wid and dao.get_incoming_by_id(incid):
            tid = dao.get_tid_from_incoming(incid)
            dao.update_transaction(tquantity, ttotal, pid, sid, rid, uid, tid)
            dao.update_incoming(wid, tid)
            tdate = dao.get_transaction_date(tid)
            attr_array = [tid, incid, tdate, tquantity, ttotal, pid, sid, rid, uid, wid]
            result = self.build_attributes_dict(attr_array, "incoming")
            return jsonify(Incoming=result)
        else:
            return jsonify(Error="Unexpected/Missing attributes in request.")
    

    #DELETE (ONLY FOR DEBUGGING)
    def delete_incoming(self, incid):
        dao = TransactionDAO()
        if not dao.get_incoming_by_id(incid):
            return jsonify(Error="Incoming transaction not found."), 404
        else:
            tid = dao.get_tid_from_incoming(incid)
            print("incoming id: " + str(incid))
            print("transaction id: "+ str(tid))
            ret_incid = dao.delete_incoming(incid)
            ret_tid = dao.delete_transaction(tid)
            print("Removed incoming: "+str(incid)+" and Transaction: "+str(tid))
            return jsonify(DeleteStatus="OK"), 200
    
    #----------------------CRUD for outgoing----------------------

    #READ-----
    def get_all_outgoing(self):
        dao = TransactionDAO()
        all_outgoing = dao.get_all_outgoing()
        result = []
        for row in all_outgoing:
            result.append(self.build_attributes_dict(row, "outgoing"))
        return jsonify(Outgoing=result)

    def get_outgoing_by_id(self, outid):
        dao = TransactionDAO()
        row = dao.get_outgoing_by_id(outid)
        if not row:
            return jsonify(Error = "Outgoing transaction not found"), 404
        else:
            outgoing = self.build_attributes_dict(row[0],"outgoing")
            return jsonify(Outgoing = outgoing)

    #CREATE-----
    def insert_outgoing(self, json):
        """
        Create outgoing transaction.
        Mutates outgoingt, transaction, warehouse,
        and rack related to transaction
        """
        KEYS_LENGTH = 8
        if len(json) != KEYS_LENGTH:
            return jsonify(Error = 'Malformed json'), 400

        tquantity = json.get('tquantity', None)
        obuyer = json.get('obuyer', None)
        ttotal = json.get('ttotal', None)
        pid = json.get('pid', None)
        sid = json.get('sid', None)
        rid = json.get('rid', None)
        uid = json.get('uid', None)
        wid = json.get('wid', None)
        try:
            self.validate_outgoing(pid, sid, rid, uid, wid, tquantity)
        except ValueError as e:
            return jsonify(Error = e.args[0]), 400

        #if not self.validate_outgoing(pid, sid, rid, uid, wid, tquantity):
        #    return jsonify(Error = 'Invalid data'), 400

        if obuyer is None:
            return jsonify(Error = 'Buyer is not set'), 400

        rack_dao = RackDAO()
        curr_quantity = rack_dao.get_rack_quantity(rid)
        if curr_quantity < tquantity:
            return jsonify(Error = 'Unable to complete transaction; \
                    Not enough parts in rack'), 400

        #mutations
        transaction_dao = outgoing_dao = TransactionDAO()
        tid = transaction_dao.insert_transaction(tquantity, ttotal, pid, sid, rid, uid)
        outid = outgoing_dao.insert_outgoing(obuyer, wid, tid)
        tdate = transaction_dao.get_transaction_date(tid)
        attr_array = [tid,outid, obuyer, wid, tdate, tquantity, ttotal, pid, sid, rid, uid]

        #update tables
        warehouse_dao = WarehouseDAO()
        new_budget = warehouse_dao.get_warehouse_budget(wid) + ttotal
        wid = warehouse_dao.set_warehouse_budget(wid, new_budget)

        new_quantity = curr_quantity - tquantity
        rid = rack_dao.set_rack_quantity(rid, new_quantity)

        result = self.build_attributes_dict(attr_array, "outgoing")
        return jsonify(Outgoing=result)



    #UPDATE-----
    def update_outgoing(self, outid, json):
        if len(json)!=8: return jsonify(Error="Unexpected/Missing attributes in request.")
        dao = TransactionDAO()
        tquantity = json.get('tquantity', None)
        ttotal = json.get('ttotal', None)
        pid = json.get('pid', None)
        sid = json.get('sid', None)
        rid = json.get('rid', None)
        uid = json.get('uid', None)
        wid = json.get('wid', None)
        obuyer = json.get('obuyer', None)
        if outid and tquantity and ttotal and pid and sid and rid and uid and wid and obuyer and dao.get_outgoing_by_id(outid):
            tid = dao.get_tid_from_outgoing(outid)
            dao.update_transaction(tquantity, ttotal, pid, sid, rid, uid, tid)
            dao.update_outgoing(outid, obuyer, wid)
            tdate = dao.get_transaction_date(tid)
            attr_array = [tid,outid, obuyer, wid, tdate, tquantity, ttotal, pid, sid, rid, uid]
            result = self.build_attributes_dict(attr_array, "outgoing")
            return jsonify(Incoming=result)
        else:
            return jsonify(Error="Unexpected/Missing attributes in request.")

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
            result.append(self.build_attributes_dict(row, "exchange"))
        return jsonify(exchange=result)
    
    def get_exchange_by_id(self, tranid):
        dao = TransactionDAO()
        row = dao.get_exchange_by_id(tranid)
        if not row:
            return jsonify(Error = "Exchange transaction not found"), 404
        else:
            result = self.build_attributes_dict(row[0], "exchange")
            return jsonify(exchange = result)
    

    #CREATE-----
    def validate_exchange(self, tquantity,ttotal,pid,sid, outgoing_rid, incoming_rid, outgoing_uid, incoming_uid, outgoing_wid, incoming_wid):
        part_dao = PartsDAO()
        supplier_dao = SupplierDAO()
        rack_dao = RackDAO()
        user_dao = UserDAO()
        warehouse_dao = WarehouseDAO()

        part_row = part_dao.getPartById(pid)
        supplier_row = supplier_dao.get_supplier_by_ID(sid)

        outgoing_rack_row = rack_dao.get_rack_by_id(outgoing_rid)
        incoming_rack_row = rack_dao.get_rack_by_id(incoming_rid)
        
        outgoing_user_row = user_dao.getUserById(outgoing_uid)
        incoming_user_row = user_dao.getUserById(incoming_uid)

        outgoing_warehouse_row = warehouse_dao.get_warehouse_by_id(outgoing_wid)
        incoming_warehouse_row = warehouse_dao.get_warehouse_by_id(incoming_wid)
        
        if not part_row:
            raise ValueError('Provided PID invalid')
        if not supplier_row:
            raise ValueError('Provided SID invalid')
        if not outgoing_rack_row:
            raise ValueError('Provided outgoing RID invalid')
        if not incoming_rack_row:
            raise ValueError('Provided incoming RID invalid')
        if not outgoing_user_row:
            raise ValueError('Provided outgoing UID invalid')
        if not incoming_user_row:
            raise ValueError('Provided incoming UID invalid')
        if not outgoing_warehouse_row:
            raise ValueError('Provided outgoing WID invalid')
        if not incoming_warehouse_row:
            raise ValueError('Provided incoming WID invalid')
        
        supid = supplier_dao.get_supply_by_sid_and_pid(sid,pid)
        if not supid:
            raise ValueError('Provided supplier does not provide this part')

        #validate user belongs to warehouse
        outgoing_user_wid = user_dao.getUserWarehouse(outgoing_uid)[0]
        if outgoing_user_wid != outgoing_wid:
            raise ValueError('User does work for given outgoing warehouse')

        incoming_user_wid = user_dao.getUserWarehouse(incoming_uid)[0]
        if incoming_user_wid != incoming_wid:
            raise ValueError('User does work for given incoming warehouse')

        outgoing_rack_pid = rack_dao.get_rack_part(outgoing_rid)[0]
        if outgoing_rack_pid != pid:
           raise ValueError('Outgoing Rack does not hold provided part')

        incoming_rack_pid = rack_dao.get_rack_part(incoming_rid)[0]
        if incoming_rack_pid != pid:
           raise ValueError('Incoming Rack does not hold provided part')
        return True


    def insert_exchange(self, json):
        if len(json)!=8: return jsonify(Error = 'Malformed json'), 400
        tquantity = json.get('tquantity', None)
        ttotal = json.get('ttotal', None)
        pid = json.get('pid', None)
        sid = json.get('sid', None)
        outgoing_rid = json.get('outgoing_rid', None)
        incoming_rid = json.get('incoming_rid', None)
        outgoing_uid = json.get('outgoing_uid', None)
        incoming_uid = json.get('incoming_uid', None)
        outgoing_wid = json.get('outgoing_wid', None)
        incoming_wid = json.get('incoming_wid', None)
        try:
            self.validate_exchange(tquantity,ttotal,pid,sid, outgoing_rid, incoming_rid, outgoing_uid, incoming_uid, outgoing_wid, incoming_wid)
        except ValueError as e:
            return jsonify(Error = e.args[0]), 400

        rack_dao = RackDAO()
        curr_quantity = rack_dao.get_rack_quantity(outgoing_rid)
        if curr_quantity < tquantity:
            return jsonify(Error = 'Unable to complete transaction; \
                    Not enough parts in rack'), 400

        dao = TransactionDAO()
        warehouse_dao = WarehouseDAO()
        supplier_dao = SupplierDAO()

        outgoing_new_budget = warehouse_dao.get_warehouse_budget(outgoing_wid) + ttotal
        warehouse_dao.set_warehouse_budget(outgoing_wid, outgoing_new_budget)

        outgoing_new_quantity = curr_quantity - tquantity
        rack_dao.set_rack_quantity(outgoing_rid, outgoing_new_quantity)

        outgoing_tid = dao.insert_transaction(tquantity, ttotal, pid, sid, outgoing_rid, outgoing_uid)
        outgoing_tranid = dao.insert_exchange(outgoing_wid, incoming_wid, outgoing_tid)
        outgoing_tdate = dao.get_transaction_date(outgoing_tid)
        outgoing_attr_array = [outgoing_tid,outgoing_tranid, outgoing_wid, incoming_wid, outgoing_tdate, tquantity, ttotal, pid, sid, outgoing_rid, outgoing_uid]

        incoming_warehouse_budget = warehouse_dao.get_warehouse_budget(incoming_wid)
        incoming_new_budget = incoming_warehouse_budget - ttotal
        warehouse_dao.set_warehouse_budget(incoming_wid, incoming_new_budget)

        incoming_new_quantity = rack_dao.get_rack_quantity(incoming_rid) + tquantity
        rack_dao.set_rack_quantity(incoming_rid, incoming_new_quantity)

        incoming_new_stock = supplier_dao.get_supplier_supplies_stock_by_sid_and_pid(sid, pid) - tquantity
        supplier_dao.edit_supplies_stock_by_sid_and_pid(sid, pid, incoming_new_stock)

        incoming_tid = dao.insert_transaction(tquantity, ttotal, pid, sid, incoming_rid, incoming_uid)
        incoming_tranid = dao.insert_exchange(outgoing_wid, incoming_wid, incoming_tid)
        incoming_tdate = dao.get_transaction_date(incoming_tid)
        incoming_attr_array = [incoming_tid,incoming_tranid, outgoing_wid, incoming_wid, incoming_tdate, tquantity, ttotal, pid, sid, incoming_rid, incoming_uid]

        outgoing_result = self.build_attributes_dict(outgoing_attr_array, "exchange")
        incoming_result = self.build_attributes_dict(incoming_attr_array, "exchange")
        result = [outgoing_result,incoming_result]
        return jsonify(exchange=result)
    
    #UPDATE-----
    def update_exchange(self, tid, json):
        return
    

    #DELETE (ONLY FOR DEBUGGING)
    def delete_exchange(self):
        return
