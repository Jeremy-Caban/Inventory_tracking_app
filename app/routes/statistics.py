from app import app
from app.handlers.warehouse import WarehouseHandler
from flask import jsonify, request


@app.route('/los-cangri/most/rack')
def get_warehouse_most_racks():
    if request.method != 'GET':
        return jsonify(Error='Not allowed'), 404
    return WarehouseHandler().get_warehouse_most_racks()

@app.route('/los-cangri/most/incoming')
def get_warehouse_most_incoming():
    if request.method != 'GET':
        return jsonify(Error = 'Not allowed'), 404
    return WarehouseHandler().get_warehouse_most_incoming()

@app.route('/los-cangri/least/outgoing')
def get_warehouse_least_outgoing():
    if request.method != 'GET':
        return jsonify(Error = 'Not allowed'), 404
    return WarehouseHandler().get_warehouse_least_outgoing()

@app.route('/los-cangri/most/city')
def get_most_city_transactions():
     if request.method != "GET":
         return jsonify(Error = 'Not allowed'), 404
     return WarehouseHandler().get_most_city_transactions()
