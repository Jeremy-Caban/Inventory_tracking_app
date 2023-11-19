from app import app
from app.handlers.warehouse import WarehouseHandler
from flask import jsonify, request


@app.route('/most/rack')
def get_warehouse_most_racks():
    if request.method != 'GET':
        return jsonify(Error='Not allowed'), 404
    return WarehouseHandler().get_warehouse_most_racks()

@app.route('/most/incoming')
def get_warehouse_most_incoming():
    if request.method != 'GET':
        return jsonify(Error = 'Not allowed'), 404
    return WarehouseHandler().get_warehouse_most_incoming()
