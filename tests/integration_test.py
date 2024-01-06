import sys
from flask import Flask
import psycopg2
import pytest
sys.path.append("/root/projects/inventory-tracking-app-los-cangris") #replace with location of project
from app.config import dbconfig


#override dbconfig variables so that one ca hook up their local database
dbconfig.host = "localhost"
dbconfig.dbname = "testdb"
dbconfig.user = "postgres"
dbconfig.password = "postgres"
dbconfig.port = "5432"

base_url = '/los-cangri/'

# List of tables to truncate
tables_to_truncate = [
    'works', 'supplies', 'inside', 'incomingt', 'outgoingt',
    'transaction', '"user"', 'supplier', 'rack', 'parts',
    'transfert', 'warehouse'
]

def reset_db():
    try:
        with psycopg2.connect(user=dbconfig.user, password=dbconfig.password, host=dbconfig.host, dbname=dbconfig.dbname, port=dbconfig.port) as conn:
            with conn.cursor() as cursor:
                for table in tables_to_truncate:
                    query = f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"
                    cursor.execute(query)
                    print(f"Truncated table {table}")
        return True
    except Exception as e:
        print(e)
        return False        

@pytest.fixture(scope="module")
def app():
    from app import app
    app.config.update({
        "TESTING": True,
    })
    
    reset_db() # start with a clean slate
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_server_running(client):
    response = client.get(base_url)
    assert b"lol" in response.data

def helper_test_posts(client, endpoint, post_data, expected_status, expected_response_structure):
    response = client.post(endpoint, json=post_data)
    assert response.status_code == expected_status, response.data

    if expected_status == 201:
        response_data = response.json
        for key, fields in expected_response_structure.items():
            #validate response structure
            assert key in response_data
            for field in fields:
                assert field in response_data[key]
                #validate data
                if field in post_data:
                    assert response_data[key][field] == post_data[field]
        return True

def validate_updates(client, endpoint, update_data, expected_status, expected_response_structure):
    response = client.put(endpoint,json=update_data)
    assert response.status_code == expected_status, response.data

    if expected_status == 200:
        response_data = response.json
        for key, fields in expected_response_structure.items():
            #validate response structure
            assert key in response_data
            for field in fields:
                assert field in response_data[key]
                #validate data
                if field in update_data:
                    assert response_data[key][field] == update_data[field]
        return True

# @pytest.mark.order(0)
@pytest.mark.parametrize("data, status_code", [
    ({"pprice": 100.0, "ptype": "Steel", "pname": "Bolt"}, 201),  # Successful case
    ({"pprice": 1.0, "ptype": "wood", "pname": "stick"}, 201),  # Successful case
    ({"pprice": 100.0, "pname": "Bolt"}, 400),  # Missing 'ptype'
    ({"pprice": "100.0", "ptype": "Steel", "pname": "Bolt"}, 400),  # Incorrect data type
    ({"pprice": -50.0, "ptype": "Steel", "pname": "Bolt"}, 400),  # Invalid value
    ({"pprice": 0.0, "ptype": "Steel", "pname": "Bolt"}, 400)  # Invalid value
])
def test_post_parts(client, data, status_code):
    expected_structure = {"Part": ["pid", "pname", "pprice", "ptype"]}
    endpoint = base_url+'part'
    helper_test_posts(client,endpoint,data,status_code, expected_structure)

# @pytest.mark.order(0)
@pytest.mark.parametrize("data, status_code", [
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":500}, 201),  # Successful case
    ({"wname":"Big Balling Warehouse", "wcity":"San Juan", "wemail":"juan@test", "wphone":"787-1DB-TEST", "budget":100000}, 201),  # Successful case
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "budget":500}, 400),  # missing 'wphone'
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":'500'}, 400),  # Incorrect data type
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":-500}, 400),  # Invalid value
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":0}, 400),  # Invalid value
    
])
def test_post_warehouse(client, data, status_code):
    expected_structure = {"Warehouse": ["wid", "wname", "wcity", "wemail", "wphone", "budget"]}
    endpoint = base_url+'warehouse'
    helper_test_posts(client,endpoint,data,status_code, expected_structure)

# @pytest.mark.order(1)
@pytest.mark.parametrize("data, status_code", [
    ({"pid":1, "pprice": 100.0, "ptype": "Steel", "pname": "Bolt"}, 200),  # Successful case
    ({"pid":99999, "pprice": 100.0, "ptype": "Steel", "pname": "Bolt"}, 404),  # Pid doesnt exist
])   
def test_get_part(client, data, status_code):
    response = client.get(base_url+f'part/{data["pid"]}')
    assert response.status_code == status_code

    if status_code==200:
        part_data = response.json.get("Part", {})
        assert part_data.get("pname") == data["pname"]
        assert part_data.get("pprice") == data["pprice"]
        assert part_data.get("ptype") == data["ptype"]
        assert part_data.get("pid") == data["pid"]

@pytest.mark.parametrize("rack_data, status_code", [
    ({"capacity": 100, "wid": 1, "quantity": 12, "pid": 1}, 201),  # Successful case
    ({"capacity": 100, "wid": 1, "quantity": 12, "pid": 1}, 400),  # rack already exists in warehouse
    ({"capacity": 0, "wid": 2, "quantity": 12, "pid": 1}, 400),  # Invalid capacity
    ({"capacity": -100, "wid": 2, "quantity": 12, "pid": 1}, 400),  # Invalid capacity
    ({"capacity": "100", "wid": 2, "quantity": 12, "pid": 1}, 400),  # Invalid capacity
    ({"capacity": 100, "quantity": 12, "pid": 1}, 400),  # Missing 'wid'
    ({"capacity": 100, "wid": 2, "quantity": 12}, 400),  # Missing 'pid'
    ({"capacity": 100, "wid": 2, "quantity": 5, "pid": 99}, 404),  # pid doesnt exist
    ({"capacity": 100, "wid": 99, "quantity": 5, "pid": 1}, 404),  # wid doesnt exist
    ({"capacity": 100, "wid": 2, "quantity": -5, "pid": 1}, 400),  # Invalid quantity
    ({"capacity": 100, "wid": 2, "quantity": "10", "pid": 1}, 400),  # Invalid quantity
    ({"capacity": 100, "wid": 2, "quantity": 1000, "pid": 1}, 400),  # Invalid quantity - capacity is smaller than qaunt
    ({"capacity": 100, "wid": 2, "quantity": 0, "pid": 1}, 201),  # Successful case
    ({"capacity": 100, "wid": 2, "quantity": 99, "pid": 2}, 201)  # Successful case
])
def test_post_rack(client, rack_data, status_code):
    endpoint = base_url+'rack'
    expected_structure = {"Rack": ["rid", "capacity", "quantity", "pid", "wid"]}
    helper_test_posts(client, endpoint, rack_data, status_code, expected_structure)

@pytest.mark.parametrize("data, status_code", [
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": 1 }, 201),  # Successful case
    ({ "fname": "derp", "lname": "bot", "uemail": "db@upr.edu", "uphone":"1-800-plz-work", "wid": 1 }, 201),  # Successful case
    ({ "fname": "Chad", "lname": "derp", "uemail": "OS@upr.edu", "uphone":"1-800-ayuda", "wid": 2 }, 201),  # Successful case
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": 99 }, 400),  # Invalid wid
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": "1" }, 400),  # Invalid wid
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST"}, 400),  # Missing 'wid'
    ({ "fname": "Cristian", "lname": "Seguinot", "uphone":"787-0DB-TEST", "wid": 1 }, 400),  # Missing 'umail'
])
def test_post_user(client, data, status_code):
    endpoint = base_url+'user'
    expected_structure = {"User": ["uid", "fname", "lname", "uemail", "uphone", "wid"]}
    helper_test_posts(client, endpoint, data, status_code, expected_structure)

@pytest.mark.parametrize("data, status_code", [
    ({ "sname":"Berrios Imports", "scity":"Moca", "sphone":"787-0DB-TEST", "semail":"test@gmail.com" }, 201),  # Successful case
    ({ "sname":"Zalic", "scity":"trujillo", "sphone":"787-000-000", "semail":"12" }, 201),  # Successful case
    ({ "scity":"Moca", "sphone":"787-0DB-TEST", "semail":"test@gmail.com" }, 400),  # Missing 'sname'
    ({ "sname":"Berrios Imports", "scity":"Moca", "semail":"test@gmail.com" }, 400),  # Missing 'scity'
])
def test_post_suppliers(client, data, status_code):
    endpoint = base_url + 'supplier'
    expected_structure = {"Supplier": ["sid", "sname", "scity", "sphone", "semail"]}
    helper_test_posts(client, endpoint, data, status_code, expected_structure)

@pytest.mark.parametrize("sid, data, status_code", [
    (1, {"stock":10, "pid":1}, 201),  # Successful case
    (1, {"stock":100, "pid":1}, 400),  # Supplier already supplies part
    (1, {"stock":10, "pid":2}, 201),  # Successful case
    (2, {"stock":0, "pid":2}, 400),  # Invalid stock
    (2, {"stock":-10, "pid":2}, 400),  # Invalid stock
    (2, {"stock":10, "pid":99}, 400),  # pid doesnt exist therefore is invalid
    (2, {"stock":10, "pid":"2"}, 400),  # Invalid pid
    (2, {"stock":"10", "pid":2}, 400),  # Invalid stock
    (2, {"stock":10, "pid":2}, 201),  # Successful case
    (2, {"stock":10, "pid":1}, 201),  # Successful case
    (9, {"stock":10, "pid":1}, 404),  # sid doesnt exist therefore cant find supplier
])
def test_supply_parts(client, sid, data, status_code):
    endpoint = base_url + f'supplier/{sid}/parts'
    expected_structure = {"Supplies": ["supid", "pid", "sid", "stock"]}
    helper_test_posts(client, endpoint, data, status_code, expected_structure)


"""
how to test transactions
- do a post
- check post 
- check if enities were affected correctly
"""

@pytest.mark.parametrize("data, status_code", [
    ({"tquantity":2,"ttotal":200,"pid":1,"sid":1,"rid":1,"uid":1,"wid":1}, 201),  # Successful case
    # test warehouse budget
    ({"tquantity":3,"ttotal":300,"pid":1,"sid":1,"rid":1,"uid":1,"wid":1}, 201),  # Successful case, note: warehouse budget is now 0
    ({"tquantity":3,"ttotal":300,"pid":1,"sid":1,"rid":1,"uid":1,"wid":1}, 400),  # Warehouse doesnt have enough budget
    # test rack quantity
    ({"tquantity":1,"ttotal":1,"pid":2,"sid":2,"rid":3,"uid":3,"wid":2}, 201),  # Successful case, note: rack had qauntity at 99, and now is 100
    ({"tquantity":1,"ttotal":1,"pid":2,"sid":2,"rid":3,"uid":3,"wid":2}, 400),  # rack is too full, note: quantity is 100 and capacity caps at 100, therefore we couldnt add one more part
    # test stock
    ({"tquantity":5,"ttotal":500,"pid":1,"sid":1,"rid":2,"uid":3,"wid":2}, 201),  # Successful case, note: stock is now 0
    ({"tquantity":5,"ttotal":500,"pid":1,"sid":1,"rid":2,"uid":3,"wid":2}, 400),  # Not enough stock
    ({"tquantity":5,"ttotal":500,"pid":1,"sid":2,"rid":2,"uid":3,"wid":2}, 201),  #Succesful case testing another supplier
    # test entity relationships
    ({"tquantity":1,"ttotal":100,"pid":1,"sid":2,"rid":2,"uid":2,"wid":2}, 400),  # User does not work in warehouse
    ({"tquantity":1,"ttotal":100,"pid":1,"sid":2,"rid":1,"uid":3,"wid":2}, 400),  # Rack doesnt exist in warehouse
    ({"tquantity":1,"ttotal":100,"pid":1,"sid":2,"rid":2,"uid":3,"wid":1}, 400),  # Wrong Warehouse 
    ({"tquantity":1,"ttotal":100,"pid":1,"sid":99,"rid":2,"uid":3,"wid":2}, 400),  # Invalid supplier
    ({"tquantity":1,"ttotal":100,"pid":2,"sid":2,"rid":2,"uid":3,"wid":2}, 400),  # Invalid Part
    ({"tquantity":1,"pid":1,"sid":2,"rid":2,"uid":3,"wid":2}, 400),  # Missing ttotaL
    ({"tquantity":1,"ttotal":100,"pid":2,"sid":2,"rid":2,"uid":3,"wid":"2"}, 400),  # Invalid wid
    ({"tquantity":1,"ttotal":100,"pid":2,"sid":2,"rid":"2","uid":3,"wid":2}, 400),  # Invalid rid
    ({"tquantity":1,"ttotal":100,"pid":2,"sid":"2","rid":2,"uid":3,"wid":2}, 400),  # Invalid sid
    ({"tquantity":1,"ttotal":"100","pid":2,"sid":2,"rid":2,"uid":3,"wid":2}, 400),  # Invalid ttotal
    ({"tquantity":"1","ttotal":100,"pid":2,"sid":2,"rid":2,"uid":3,"wid":2}, 400),  # Invalid tqauntity
    ({"tquantity":1,"ttotal":100,"pid":1,"sid":2,"rid":2,"uid":3,"wid":2}, 201),  # Successful case

])
def test_post_transaction(client, data, status_code):
    from app.dao import parts, rack, warehouse, supplier
    pid = data.get('pid',None)
    wid =  data.get('wid',None)
    rid =  data.get('rid',None)
    sid =  data.get('sid',None)
    
    pprice = parts.PartsDAO().get_part_price(pid)
    budget = warehouse.WarehouseDAO().get_warehouse_budget(wid)
    rack_quant = rack.RackDAO().get_rack_quantity(rid)
    stock = supplier.SupplierDAO().get_supplier_supplies_stock_by_sid_and_pid(sid,pid)

    endpoint = base_url + 'incoming'
    expected_structure = {"Incoming": ["icid", "tdate", "tquantity", "ttotal", "uid", "wid", "rid", "pid", "sid", "tid"]}
    if not helper_test_posts(client, endpoint, data, status_code, expected_structure): 
        return
    tquant = data['tquantity']
    assert warehouse.WarehouseDAO().get_warehouse_budget(wid) == budget - pprice*tquant
    assert rack.RackDAO().get_rack_quantity(rid) == rack_quant+tquant
    assert supplier.SupplierDAO().get_supplier_supplies_stock_by_sid_and_pid(sid,pid) == stock - tquant


@pytest.mark.parametrize("data, status_code", [
    # testing parts in rack
    ({"tquantity":17,"obuyer":"Test","ttotal":1700,"pid":1,"sid":1,"rid":1,"uid":1,"wid":1}, 201),  # Successful case
    ({"tquantity":1,"obuyer":"Test","ttotal":100,"pid":1,"sid":1,"rid":1,"uid":1,"wid":1}, 400),  # not enough parts in rack
    # testing relationships
    ({"tquantity":1,"obuyer":"Test","ttotal":100,"pid":2,"sid":1,"rid":2,"uid":3,"wid":2}, 400),  # invalid pid
    ({"tquantity":1,"obuyer":"Test","ttotal":100,"pid":1,"sid":1,"rid":3,"uid":3,"wid":2}, 400),  # invalid rack
    ({"tquantity":1,"obuyer":"Test","ttotal":100,"pid":1,"sid":1,"rid":2,"uid":2,"wid":2}, 400),  # invalid user
    ({"tquantity":1,"obuyer":"Test","ttotal":100,"pid":1,"sid":1,"rid":2,"uid":3,"wid":1}, 400),  # invalid warehouse
    ({"tquantity":"1","obuyer":"Test","ttotal":100,"pid":1,"sid":1,"rid":2,"uid":3,"wid":2}, 400),  # invalid quantity
    ({"tquantity":1,"ttotal":100,"pid":1,"sid":1,"rid":2,"uid":3,"wid":2}, 400),  # Missing obuyer
    ({"tquantity":1,"obuyer":"Test","ttotal":100,"pid":1,"sid":1,"rid":2,"uid":3,"wid":2}, 201),  # Succesful case

])
def test_post_outgoing_transaction(client, data, status_code):
    from app.dao import parts, rack, warehouse, supplier
    pid = data.get('pid',None)
    wid =  data.get('wid',None)
    rid =  data.get('rid',None)
    profit_yield = 1.10
    
    pprice = parts.PartsDAO().get_part_price(pid)
    budget = warehouse.WarehouseDAO().get_warehouse_budget(wid)
    rack_quant = rack.RackDAO().get_rack_quantity(rid)

    endpoint = base_url + 'outgoing'
    expected_structure = {"Outgoing": ["outid", "tdate", "tquantity", "ttotal", "uid", "wid", "rid", "pid", "sid", "tid", "obuyer"]}
    if not helper_test_posts(client, endpoint, data, status_code, expected_structure): 
        return
    tquant = data.get('tquantity')
    print(warehouse.WarehouseDAO().get_warehouse_budget(wid),budget, pprice*tquant*profit_yield )
    assert warehouse.WarehouseDAO().get_warehouse_budget(wid) == (budget + pprice*tquant*profit_yield)
    assert rack.RackDAO().get_rack_quantity(rid) == rack_quant-tquant
    assert rack.RackDAO().get_rack_quantity(rid) >=0

@pytest.mark.parametrize("pid, data, status_code", [
    # testing parts in rack
    (1, {"pprice":111, "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 200),  # Successful case
    (1, {"pprice":0, "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 400),  # Invalid pprice
    (1, {"pprice":-50, "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 400),  # Invalid pprice
    (1, {"pprice":"50", "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 400),  # Invalid pprice
    (1, {"pprice":50, "ptype":"", "pname":"amd cpu ryzen flop"}, 400),  # invalid ptype
])    
def test_update_part(client, pid, data, status_code):
    expected_structure = {"Part": ["pid", "pname", "pprice", "ptype"]}
    endpoint = base_url+f'part/{pid}'
    validate_updates(client, endpoint,data,status_code, expected_structure)
    