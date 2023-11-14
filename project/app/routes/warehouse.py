from app import app
from app.handlers.warehouse import WarehouseHandler
from flask import jsonify, request

#TODO(xavier) Finish implementing all warehouse routes and ohter functionality.

@app.route('/warehouse', methods=['GET', 'POST'])
def getAllWarehouses():
    if request.method == 'POST':
        print(request.json)
        return WarehouseHandler().insert_warehouse(request.json)
    return WarehouseHandler().get_all_warehouses()

@app.route('/warehouse/<int:wid>',
           methods=['GET','POST'])
def get_warehouse_by_id(wid):
    if request.method == 'GET':
        return WarehouseHandler().get_warehouse_by_id(wid)
    else:
        return jsonify(Error = "Not implemented"), 501

@app.route('/warehouse/<string:wname>')
def get_warehouse_by_name(wname):
    if request.method == 'GET':
        return WarehouseHandler().get_warehouse_by_name(str(wname))
    else:
        return jsonify(Error = "Not implemented"), 501

