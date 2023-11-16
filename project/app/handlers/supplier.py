from flask import jsonify
from app.dao.supplier import SupplierDAO


class SupplierHandler:
    #-----Helper methods-----
    
    def build_supplier_attributes(self, sid, sname, scity, sphone, semail):
        return {
                'sid':sid,
                'sname':sname,
                'scity':scity,
                'semail':semail,
                'sphone':sphone
                }

    def build_supplier_dict(self, rows):
        keys = ['sid', 'scity', 'sname', 'sphone','semail']
        return dict(zip(keys, rows))

    #-----Helper methods END-----

    #works!, if more attributes are added, add them in ORDER to the keys array in build_supplier_dict
    def get_all_suppliers(self): 
        dao = SupplierDAO()
        all_suppliers = dao.get_all_suppliers()
        result = []
        
        for row in all_suppliers:
            result.append(self.build_supplier_dict(row))
        return jsonify(Suppliers=result)
    
    #works!, if more attributes are added, add them in ORDER to the keys array in build_supplier_attributes
    def insert_supplier(self, json): #works
        KEYS_LENGTH = 4
        if len(json) == KEYS_LENGTH:
            sname = json.get('sname', None)
            scity = json.get('scity', None)
            sphone = json.get('sphone', None)
            semail = json.get('semail', None)
            #Check every info is being sent by json
            if sname and scity and sphone and semail:
                dao = SupplierDAO()
                sid = dao.insert(sname, scity, sphone, semail)
                result = self.build_supplier_attributes(sid, sname, scity, sphone, semail)
                return jsonify(Supplier=result), 201
        return jsonify(Error="Unexpected/Missing attributes in request.")
    
    #works!
    def get_supplier_by_id(self, sid):
        dao = SupplierDAO()
        row = dao.get_supplier_by_ID(sid)
        if not row:
            return jsonify(Error = "Supplier not found"), 404
        else:
            supplier = self.build_supplier_dict(row[0]) #note: get_supplier_by_ID returns a list of rows
            print(row)
            print(supplier)
            return jsonify(Supplier = supplier)
    
    #works!
    def update_supplier(self, sid, json):
        KEYS_LENGTH = 4         #keep this updated with the number of attributes that are allowed to be edited 
        dao = SupplierDAO()
        if not dao.get_supplier_by_ID(sid):
            return jsonify(Error='Supplier not found'), 404
        if len(json) != KEYS_LENGTH:
            return jsonify(Error=f'Malformed data: got {len(json)}')
        sname = json.get('sname', None)
        scity = json.get('scity', None)
        semail = json.get('semail',None)
        sphone = json.get('sphone', None)
        
        #Check every info is being sent by json
        if sname and scity and semail and sphone:
            dao.update(sid, scity, sname, sphone, semail)
            result = self.build_supplier_attributes(sid, sname, scity, sphone, semail)
            return jsonify(Supplier=result), 201
        return jsonify(Error='Attributes were not set properly')
    
    #works!
    def delete_supplier(self, sid):
        dao = SupplierDAO()
        if not dao.get_supplier_by_ID(sid):
            return jsonify(Error="Supplier not found"), 404
        response = dao.delete(sid)
        return jsonify(DeletedStatus='OK',row=response), 200
    
    #unused
    # #works!
    # def get_supplier_by_name(self, sname):
    #     dao = SupplierDAO()
    #     supplier_by_city = dao.get_supplier_by_name(sname)
    #     if not supplier_by_city:
    #         return jsonify(Error = "No suppliers with that name"), 404
    #     result = []
    #     for row in supplier_by_city:
    #         result.append(self.build_supplier_dict(row))
    #     return jsonify(SuppliersByName=result)
    
    # #works!
    # def get_supplier_by_city(self, scity):
    #     dao = SupplierDAO()
    #     supplier_by_city = dao.get_supplier_by_city(scity)
    #     if not supplier_by_city:
    #         return jsonify(Error = "No suppliers in that city"), 404
    #     result = []
    #     for row in supplier_by_city:
    #         result.append(self.build_supplier_dict(row))
    #     return jsonify(SuppliersByCity=result)