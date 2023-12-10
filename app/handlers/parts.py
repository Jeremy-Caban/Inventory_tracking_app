from flask import jsonify
from app.dao.parts import PartsDAO


class PartHandler:
    def build_part_dict(self, row):
        result = {}
        result['pid'] = row[0]
        result['pprice'] = row[1]
        result['ptype'] = row[2]
        result['pname'] = row[3]
        return result

    def build_part_attributes(self, pid, pprice, ptype, pname):
        result = {}
        result['pid'] = pid
        result['pprice'] = pprice
        result['ptype'] = ptype
        result['pname'] = pname
        return result

    def getAllParts(self):
        dao = PartsDAO()
        parts_list = dao.getAllParts()
        result_list = []
        for row in parts_list:
            result = self.build_part_dict(row)
            result_list.append(result)
        return jsonify(Parts=result_list)

    def getPartById(self, pid):
        dao = PartsDAO()
        row = dao.getPartById(pid)
        if not row:
            return jsonify(Error="Part Not Found"), 404
        else:
            part = self.build_part_dict(row)
            return jsonify(Part=part)

    def searchParts(self, args):
        pprice = args.get("pprice")
        ptype = args.get("ptype")
        pname = args.get("pname")
        dao = PartsDAO()
        parts_list = []
        if (len(args) == 2) and pprice and ptype:
            parts_list = dao.getPartsByPriceAndType(pprice, ptype)
        elif (len(args) == 1) and pprice:
            parts_list = dao.getPartsByPrice(pprice)
        elif (len(args) == 1) and ptype:
            parts_list = dao.getPartsByType(ptype)
        elif (len(args) == 1) and pname:
            parts_list = dao.getPartsByName(pname)
        else:
            return jsonify(Error="Malformed query string"), 400

        result_list = []
        for row in parts_list:
            result = self.build_part_dict(row)
            result_list.append(result)
        return jsonify(Parts=result_list)

    def insertPart(self, form):
        print("form: ", form, 'len ', len(form.request))
        if len(form) != 3:
            return jsonify(Error="Malformed post request"), 400
        else:
            pprice = form["pprice"]
            ptype = form["ptype"]
            pname = form["pname"]
            if not isinstance(pprice, (int, float)) or not isinstance(ptype, str) or not isinstance(pname, str):
                return jsonify("Error. Incorrect attribute type."), 400
            elif pprice < 0 or len(ptype) > 100 or len(pname) > 100:
                return jsonify("Error. Incorrect attribute range."), 400
            if pprice and ptype and pname:
                dao = PartsDAO()
                pid = dao.insert(pprice, ptype, pname)
                result = self.build_part_attributes(
                    pid, pprice, ptype, pname
                )
                return jsonify(Part=result), 201
            else:
                return jsonify(Error="Unexpected attributes in post request"), 400

    def insertPartJson(self, json):
        if len(json) != 3: return jsonify(Error="Malformed Post request"), 400
        pprice = json['pprice']
        ptype = json['ptype']
        pname = json['pname']
        if not isinstance(pprice, (int, float)) or not isinstance(ptype, str) or not isinstance(pname, str):
            return jsonify("Error. Incorrect attribute type."), 400
        elif pprice < 0 or len(ptype) > 100 or len(pname) > 100:
            return jsonify("Error. Incorrect attribute range."), 400
        if (pprice >= 0) and ptype and pname:
            dao = PartsDAO()
            pid = dao.insert(pprice, ptype, pname)
            result = self.build_part_attributes(pid, pprice, ptype, pname)
            return jsonify(Part=result), 201
        else:
            return jsonify(Error="Unexpected attributes in post request"), 400
        
    def deletePart(self, pid):
        dao = PartsDAO()
        result = dao.delete(pid)
        if result == -1:
            return jsonify("Error. Part {pid} cannot be deleted because it is still referenced in a rack."), 400
        elif result:
            return jsonify(DeleteStatus="OK"), 200
        else:
            return jsonify(Error="Part not found."), 404

    def updatePart(self, pid, json):
        dao = PartsDAO()
        if not dao.getPartById(pid):
            return jsonify(Error="Part not found."), 404
        else:
            if len(json) != 3:
                return jsonify(Error="Malformed update request"), 400
            else:
                pprice = json['pprice']
                ptype = json['ptype']
                pname = json['pname']

                if not isinstance(pprice, (int, float)) or not isinstance(ptype, str) or not isinstance(pname, str):
                    return jsonify("Error. Incorrect attribute type."), 400
                elif pprice < 0 or len(ptype) > 100 or len(pname) > 100:
                    return jsonify("Error. Incorrect attribute range."), 400
                if (pprice >= 0) and ptype and pname:
                    dao.update(pid, pprice, ptype, pname)
                    result = self.build_part_attributes(pid, pprice, ptype, pname)
                    return jsonify(Part=result), 200
                else:
                    return jsonify(Error="Unexpected attributes in update request"), 400
