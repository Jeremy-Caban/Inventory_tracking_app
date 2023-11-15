from flask import jsonify
from app.handlers.warehouse import WarehouseHandler
from app.dao.rack import RackDAO
from app.dao.warehouse import WarehouseDAO

#TODO(xavier)
class RackHandler:
    def build_rack_dict(self, rows):
        keys = ['rid','capacity','wid']
        return dict(zip(keys, rows))

    def build_rack_attributes(self, rid, capacity, wid):
        return {
                'rid':rid,
                'capacity': capacity,
                'wid':wid,
                }

    def get_all_racks(self):
        dao = RackDAO()
        rack_list = dao.get_all_racks()
        result = [self.build_rack_dict(row) for row in rack_list]
        return jsonify(Racks=result)

    def get_rack_by_id(self, rid):
        dao = RackDAO()
        row = dao.get_rack_by_id(rid)
        if not row:
            return jsonify(Error = "Rack not found"), 404
        else:
            rack = self.build_rack_dict(row)
            return jsonify(Rack = rack)

    def insert_rack(self, json):
        capacity = json.get('capacity', 0)
        wid = json.get('wid', None)
        if wid is None or not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Provided warehouse ID not found.')
        if capacity == 0:
            return jsonify(Error='Rack capacity cannot be 0.')
        dao = RackDAO()
        rid = dao.insert(capacity, wid)
        result = self.build_rack_attributes(rid, capacity, wid)
        return jsonify(Rack=result), 201

    def update_rack(self, rid, form):
        KEYS_LENGTH = 3
        dao = RackDAO()
        if not dao.get_rack_by_id(rid):
            return jsonify(Error='Rack not found'), 404
        if len(form) != KEYS_LENGTH:
            return jsonify(Error=f'Malformed data: got {len(form)}')
        capacity = json.get('capacity', 0)
        wid = json.get('wid', None)
        #TODO(xavier) add error code
        if wid is None or not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Provided warehouse ID not found.')
        if capacity == 0:
            return jsonify(Error='Rack capacity cannot be 0.')
        dao.update(rid, capacity, wid)
        result = self.build_rack_attributes(rid,capacity,wid)
        return jsonify(Rack=result), 201

    #TODO(xavier) have to make sure rack does not have parts
    def delete_rack(self, rid):
        dao = RackDAO()
        if not dao.get_rack_by_id(rid):
            return jsonify(Error="Rack not found"), 404
        if len(dao.get_parts_in_rack(rid)) == 0:
            return jsonify(Error="Cannot delete non empty rack")
        response = dao.delete(rid)
        return jsonify(DeletedStatus='OK',row=response), 200




