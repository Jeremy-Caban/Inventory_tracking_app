from flask import jsonify
from app.handlers.warehouse import WarehouseHandler
from app.dao.rack import RackDAO
from app.dao.warehouse import WarehouseDAO
from app.dao.parts import PartsDAO
from app.dao.user import UserDAO


# TODO(xavier)
class RackHandler:
    def build_rack_dict(self, rows):
        keys = ['rid', 'capacity', 'quantity', 'pid', 'wid']
        return dict(zip(keys, rows))

    def build_rack_attributes(self, rid, capacity, quantity, pid, wid):
        return {
            'rid': rid,
            'capacity': capacity,
            'quantity': quantity,
            'pid': pid,
            'wid': wid
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
            return jsonify(Error="Rack not found"), 404
        else:
            rack = self.build_rack_dict(row)
            return jsonify(Rack=rack)

    def get_warehouse_rack_lowstock(self, wid, json, amount=5):
        dao = RackDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse.'), 403
        rack_list = dao.get_warehouse_racks_lowstock(wid, amount)
        result = [self.build_rack_dict(row) for row in rack_list]
        return jsonify(Racks=result)

    def get_most_expensive_racks(self, wid, json, amount=5):
        dao = RackDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse.'), 403
        rack_list = dao.get_most_expensive_racks(wid, amount)
        result = [self.build_rack_dict(row) for row in rack_list]
        return jsonify(Racks=result)

    def insert_rack(self, json):
        capacity = json.get('capacity', 0)
        wid = json.get('wid', None)
        quantity = json.get('quantity', 0)
        pid = json.get('pid', None)

        if wid is None or not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Provided warehouse ID not found.')
        if capacity == 0:
            return jsonify(Error='Rack capacity cannot be 0.')

        if pid is not None and PartsDAO().getPartById(pid) is None:
            return jsonify(Error='Part does not exist'), 404

        dao = RackDAO()
        rid = dao.insert(capacity, quantity, pid, wid)
        result = self.build_rack_attributes(rid, capacity, quantity, pid, wid)
        return jsonify(Rack=result), 201

    # Assume that if quantity field is not set, user meant for it to be 0
    def update_rack(self, rid, form):
        KEYS_LENGTH = 4
        dao = RackDAO()
        if not dao.get_rack_by_id(rid):
            return jsonify(Error='Rack not found'), 404
        if len(form) != KEYS_LENGTH:
            return jsonify(Error=f'Malformed data: got {len(form)}')
        capacity = form.get('capacity', 0)
        wid = form.get('wid', None)
        quantity = form.get('quantity', 0)
        pid = form.get('pid', None)

        # TODO(xavier) handle having no pid but having quantity
        if wid is None or not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Provided warehouse ID not found.'), 404
        if capacity == 0:
            return jsonify(Error='Rack capacity cannot be 0.')
        if pid is not None and PartsDAO().getPartById(pid) is None:
            return jsonify(Error='Part does not exist'), 404
        dao.update(rid, capacity, quantity, pid, wid)
        result = self.build_rack_attributes(rid, capacity, quantity, pid, wid)
        return jsonify(Rack=result), 201

    # TODO(xavier) have to make sure rack does not have parts
    def delete_rack(self, rid):
        dao = RackDAO()
        if not dao.get_rack_by_id(rid):
            return jsonify(Error="Rack not found"), 404
        if len(dao.get_parts_in_rack(rid)) == 0:
            return jsonify(Error="Cannot delete non empty rack")
        response = dao.delete(rid)
        return jsonify(DeletedStatus='OK', row=response), 200
