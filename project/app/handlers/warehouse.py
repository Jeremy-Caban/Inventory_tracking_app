from flask import jsonify
from app.dao.warehouse import WarehouseDAO

#TODO(xavier)
class WarehouseHandler:
    def build_warehouse_dict(self, rows):
        keys = ['wid', 'budget', 'wname', 'wcity', 'wemail', 'wphone']
        return dict(zip(keys, rows))

    def build_warehouse_attributes(self, wid, wname, wcity, wemail, wphone, budget):
        return {
                'wid':wid,
                'budget': budget,
                'wname':wname,
                'wcity':wcity,
                'wemail':wemail,
                'wphone':wphone
                }

    #Used for routes where we want wid and a count of most something
    def build_most_dict(self, rows):
        keys = ['wid', 'count']
        return dict(zip(keys, rows))

    def get_all_warehouses(self):
        dao = WarehouseDAO()
        warehouse_list = dao.get_all_warehouses()
        result = [self.build_warehouse_dict(row) for row in warehouse_list]
        return jsonify(Warehouses=result)

    def get_warehouse_by_id(self, wid):
        dao = WarehouseDAO()
        row = dao.get_warehouse_by_id(wid)
        if not row:
            return jsonify(Error = "Warehouse not found"), 404
        else:
            row = row[0]
            warehouse = self.build_warehouse_dict(row)
            return jsonify(Warehouse = warehouse)

    def get_warehouse_by_name(self, wname):
        dao = WarehouseDAO()
        row = dao.get_warehouse_by_name(wname)
        if not row:
            return jsonify(Error = "Warehouse not found"), 404
        else:
            warehouse = self.build_warehouse_dict(row)
            return jsonify(Warehouse = warehouse)

    #amount specified in project specs
    def get_warehouse_most_racks(self,amount=10):
        dao = WarehouseDAO()
        rack_list = dao.get_warehouse_most_racks(amount)
        if not rack_list:
            return jsonify(Error = 'Warehouses not found'), 404
        else:
            result = [self.build_most_dict(row) for row in rack_list]
            return jsonify(Warehouses=result)

    def get_warehouse_most_incoming(self, amount=5):
        dao = WarehouseDAO()
        warehouse_list = dao.get_warehouse_most_incoming(amount)
        result = [self.build_most_dict(row) for row in warehouse_list]
        return jsonify(Warehouses=result)

    def get_warehouse_least_outgoing(self, amount=3):
        dao = WarehouseDAO()
        warehouse_list = dao.get_warehouse_least_outgoing(amount)
        #use most even though its least, works the same(bad name)
        result = [self.build_most_dict(row) for row in warehouse_list]
        return jsonify(Warehouses=result)


    def insert_warehouse(self, json):
        wname = json.get('wname', None)
        wcity = json.get('wcity', None)
        wemail = json.get('wemail',None)
        wphone = json.get('wphone', None)
        budget = json.get('budget', 0)
        if wname and wcity:
            dao = WarehouseDAO()
            wid = dao.insert(wname, wcity, wemail, wphone, budget, )
            result = self.build_warehouse_attributes(wid, wname, wcity,
                                                     wemail, wphone, budget)
            return jsonify(Warehouse=result), 201
        return jsonify(Error="Unexpected/Missing attributes in request.")

    def update_warehouse(self, wid, form):
        KEYS_LENGTH = 6
        dao = WarehouseDAO()
        if not dao.get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        if len(form) != KEYS_LENGTH:
            return jsonify(Error=f'Malformed data: got {len(form)}')
        wname = form.get('wname', None)
        wcity = form.get('wcity', None)
        wemail = form.get('wemail',None)
        wphone = form.get('wphone', None)
        budget = form.get('budget', 0)

        #Assuming if other fields weren't set it was on purpose
        if wname and wcity:
            dao.update(wid, wname, wcity, wemail, wphone, budget)
            result = self.build_warehouse_attributes(wid,
                                                wname,
                                                wcity,
                                                wemail,
                                                wphone,
                                                budget
                                                )
            return jsonify(Warehouse=result), 201
        return jsonify(Error='Attributes were not set properly')

    def delete_warehouse(self, wid):
        dao = WarehouseDAO()
        if not dao.get_warehouse_by_id(wid):
            return jsonify(Error="Warehouse not found"), 404
        response = dao.delete(wid)
        return jsonify(DeletedStatus='OK',row=response), 200




