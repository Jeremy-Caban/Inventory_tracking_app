from app import app
from app.handlers.warehouse import WarehouseHandler
from app.handlers.rack import RackHandler
from app.handlers.supplier import SupplierHandler
from flask import jsonify, request


# TODO(xavier) Finish implementing all warehouse routes and other functionality.

@app.route('/warehouse', methods=['GET', 'POST'])
def getAllWarehouses():
    if request.method == 'POST':
        print(request.json)
        return WarehouseHandler().insert_warehouse(request.json)
    return WarehouseHandler().get_all_warehouses()


@app.route('/warehouse/<int:wid>',
           methods=['GET', 'PUT', 'DELETE'])
def get_warehouse_by_id(wid):
    if request.method == 'GET':
        return WarehouseHandler().get_warehouse_by_id(wid)
    elif request.method == 'PUT':
        return WarehouseHandler().update_warehouse(wid, request.form)
    elif request.method == 'DELETE':
        return WarehouseHandler().delete_warehouse(wid)
    else:
        return jsonify(Error="Not implemented"), 501


@app.route('/warehouse/<string:wname>')
def get_warehouse_by_name(wname):
    if request.method == 'GET':
        return WarehouseHandler().get_warehouse_by_name(str(wname))
    else:
        return jsonify(Error="Not implemented"), 501


@app.route('/warehouse/<int:wid>/rack/lowstock', methods=['POST'])
def get_warehouse_rack_lowstock(wid):
    if request.method == "POST":
        print(request.json)
        if not request.json or request.json.get('User_id', None) is None:
            return jsonify(Error="User ID not provided."), 403
        return RackHandler().get_warehouse_rack_lowstock(wid, request.json)
    else:
        return jsonify(Error="Not implemented"), 501


@app.route('/warehouse/<int:wid>/rack/expensive', methods=['POST'])
def get_most_expensive_racks(wid):
    if request.method == "POST":
        print(request.json)
        if not request.json or request.json.get('User_id', None) is None:
            return jsonify(Error="User ID not provided."), 403
        return RackHandler().get_most_expensive_racks(wid, request.json)
    else:
        return jsonify(Error="Not implemented"), 501


@app.route('/warehouse/<int:wid>/rack/material', methods=['POST'])
def get_warehouse_rack_bottom_material(wid):
    if request.method == "POST":
        if not request.json or request.json.get('User_id', None) is None:
            return jsonify(Error="User ID not provided."), 403
        return RackHandler().get_warehouse_rack_bottom_material(wid, request.json)
    else:
        return jsonify(Error="Not implemented"), 501

@app.route('/warehouse/<int:wid>/transaction/suppliers', methods=['POST'])
def get_warehouse_top_suppliers(wid):
    if request.method == "POST":
        if not request.json or request.json.get('User_id',None) is None:
            return jsonify(Error="User ID not provided."), 403
        return SupplierHandler().get_top_suppliers_for_warehouse(wid, request.json)
