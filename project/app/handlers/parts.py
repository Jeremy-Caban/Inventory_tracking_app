from flask import jsonify
from app.dao.parts import PartsDAO


class PartHandler:
    def build_part_dict(self, row):
        result = {}
        result['pid'] = row[0]
        result['pdate'] = row[1]
        result['pprice'] = row[2]
        result['ptype'] = row[3]
        return result

    def build_part_attributes(self, pid, pprice, ptype):
        result = {}
        result['pid'] = pid
        result['pprice'] = pprice
        result['ptype'] = ptype
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
        dao = PartsDAO()
        parts_list = []
        if (len(args) == 2) and pprice and ptype:
            parts_list = dao.getPartsByPriceAndType(pprice, ptype)
        elif (len(args) == 1) and pprice:
            parts_list = dao.getPartsByPrice(pprice)
        elif (len(args) == 1) and ptype:
            parts_list = dao.getPartsByType(ptype)
        else:
            return jsonify(Error="Malformed query string"), 400

        result_list = []
        for row in parts_list:
            result = self.build_part_dict(row)
            result_list.append(result)
        return jsonify(Parts=result_list)

    def insertPart(self, form):
        print("form: ", form)
        if len(form) != 2:
            return jsonify(Error="Malformed post request"), 400
        else:
            pprice = form["pprice"]
            ptype = form["ptype"]
            if pprice and ptype:
                dao = PartsDAO()
                pid = dao.insert(pprice, ptype)
                result = self.build_part_attributes(
                    pid, pprice, ptype
                )
                return jsonify(Part=result), 201
            else:
                return jsonify(Error="Unexpected attributes in post request"), 400

    def deletePart(self, pid):
        dao = PartsDAO()
        if not dao.getPartById(pid):
            return jsonify(Error="Part not found."), 404
        else:
            dao.delete(pid)
            return jsonify(DeleteStatus="OK"), 200

    def updatePart(self, pid, form):
        dao = PartsDAO()
        if not dao.getPartById(pid):
            return jsonify(Error="Part not found."), 404
        else:
            if len(form) != 2:
                return jsonify(Error="Malformed update request"), 400
            else:
                pprice = form['pprice']
                ptype = form['ptype']
                if pprice and ptype:
                    dao.update(pid, pprice, ptype)
                    result = self.build_part_attributes(pid, pprice, ptype)
                    return jsonify(Part=result), 200
                else:
                    return jsonify(Error="Unexpected attributes in update request"), 400
