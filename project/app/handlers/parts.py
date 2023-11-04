from flask import jsonify
from app.dao.parts import PartsDAO


class PartHandler:

    def getAllParts(self):
            dao = PartsDAO()
            parts_list = dao.getAllParts()
            result_list = []
            for row in parts_list:
                result = self.build_part_dict(row)
                result_list.append(result)
            return jsonify(Parts=result_list)