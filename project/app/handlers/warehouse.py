from flask import jsonify
from app.dao.warehouse import WarehouseDAO

#TODO(xavier)
class WarehouseHandler:
    def get_all_warehouses(self):
        print('hit handler')
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

