from flask import jsonify
from app.dao.warehouse import WarehouseDAO

#TODO(xavier)
class WarehouseHandler:
    def build_warehouse_dict(self, rows):
        keys = ['wid', 'wname', 'wcity', 'wemail','wphone','budget']
        return dict(zip(keys, rows))

    def build_warehouse_attributes(self, wid, wname, wcity, wemail, wphone, wbudget):
        return {
                'wid':wid,
                'wname':wname,
                'wcity':wcity,
                'wemail':wemail,
                'wphone':wphone,
                'wbudget':wbudget
                }

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
            result = [self.build_warehouse_dict(row) for row in rack_list]
            return jsonify(Warehouses=result)

    def insert_warehouse(self, json):
        wname = json.get('wname', None)
        wcity = json.get('wcity', None)
        wemail = json.get('email',None)
        wphone = json.get('wphone', None)
        budget = json.get('budget', 0)
        if wname and wcity:
            dao = WarehouseDAO()
            wid = dao.insert(wname, wcity, wemail, wphone, budget, )
            result = self.build_warehouse_attributes(wid, wname, wcity,
                                                     wemail, wphone, budget)
            return jsonify(Warehouse=result), 201
        return jsonify(Error="Unexpected/Missing attributes in request.")


