from flask import jsonify
from app.handlers.warehouse import WarehouseHandler
from app.dao.rack import RackDAO
from app.dao.warehouse import WarehouseDAO
from app.dao.parts import PartsDAO
from app.dao.user import UserDAO


class RackHandler:
    def build_rack_dict(self, rows):
        keys = ['rid', 'capacity', 'wid', 'quantity', 'pid']
        return dict(zip(keys, rows))

    def build_rack_attributes(self, rid, capacity, quantity, pid, wid):
        return {
            'rid': rid,
            'capacity': capacity,
            'quantity': quantity,
            'pid': pid,
            'wid': wid
        }

    def build_bottom_material(self, rows):
        keys = ['ptype', 'count']
        return dict(zip(keys, rows))

    def get_all_racks(self):
        dao = RackDAO()
        rack_list = dao.get_all_racks()
        if rack_list:
            result = [self.build_rack_dict(row) for row in rack_list]
            return jsonify(Racks=result)
        else:
            return jsonify("No racks found."), 404

    def get_rack_by_id(self, rid):
        dao = RackDAO()
        row = dao.get_rack_by_id(rid)
        if not row:
            return jsonify(Error="Rack not found"), 404
        else:
            row = row[0]
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
        rack_list = dao.get_most_expensive_racks2(wid)
        result = [{"rid":row[0], "total_price":row[1]} for row in rack_list]
        return jsonify(Racks=result)

    def get_warehouse_rack_bottom_material(self, wid, json, amount=3):
        dao = RackDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse'), 403
        rack_list = dao.get_warehouse_rack_bottom_material(wid, amount)
        result = [self.build_bottom_material(row) for row in rack_list]
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

        result1 = RackDAO().rack_in_warehouse_validation(wid, pid)
        if result1 is None:
            return jsonify(f"A Rack with part {pid} is already in Warehouse {wid}."), 400

        if not isinstance(capacity, int) or not isinstance(pid, int) or not isinstance(quantity, int) or not isinstance(wid, int):
            return jsonify("Error: Incorrect attribute type or length."), 400

        if capacity and (0 <= quantity <= capacity) and pid and wid:
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
        if capacity < quantity:
            return jsonify(Error='Quantity cannot be greater than capacity.'), 400

        result1 = RackDAO.update_rack_in_warehouse_validation()
        if result1 is None:
            return jsonify(f"A Rack with part {pid} is already in Warehouse {wid}."), 400

        if not isinstance(capacity, int) or not isinstance(pid, int) or not isinstance(quantity, int) or not isinstance(
                wid, int):
            return jsonify("Error: Incorrect attribute type or length."), 400

        if capacity and (0 <= quantity <= capacity) and pid and wid:
            flag = dao.update(rid, capacity, quantity, pid, wid)
            result = self.build_rack_attributes(rid, capacity, quantity, pid, wid)
            if flag:
                return jsonify(Rack=result), 201
            else:
                return jsonify("Not Found."), 404
            return jsonify("Unexpected attribute values."), 400

    # TODO(xavier) have to make sure rack does not have parts
    def delete_rack(self, rid):
        dao = RackDAO()
        if not dao.get_rack_by_id(rid):
            return jsonify(Error="Rack not found"), 404
        if len(dao.get_parts_in_rack(rid)) == 0:
            return jsonify(Error="Cannot delete non empty rack")
        response = dao.delete(rid)
        if response == -1:
            return jsonify(Error=f"Rack {rid} cannot be deleted because it is still referenced in transaction."), 400
        elif response:
            return jsonify(DeletedStatus='OK', row=response), 200
