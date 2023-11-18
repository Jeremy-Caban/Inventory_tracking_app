from flask import jsonify
from app.dao.user import UserDAO


# Leamsi working here
class UserHandler:

    def build_user_dict(self, row):
        result = {}
        result['uid'] = row[0]
        result['fname'] = row[1]
        result['lname'] = row[2]
        result['uemail'] = row[3]
        result['uphone'] = row[4]
        return result

    def build_user_attributes(self, uid, fname, lname, uemail, uphone):
        result = {}
        result['uid'] = uid
        result['fname'] = fname
        result['lname'] = lname
        result['uemail'] = uemail
        result['uphone'] = uphone
        return result

    def getAllUsers(self):
        dao = UserDAO()
        user_list = dao.getAllUsers()
        result_list = []
        for row in user_list:
            result = self.build_user_dict(row)
            result_list.append(result)
        return jsonify(Parts=result_list)

    def getUserById(self, uid):
        dao = UserDAO()
        row = dao.getUserById(uid)
        if not row:
            return jsonify(Error="Part Not Found"), 404
        else:
            user = self.build_user_dict(row)
            return jsonify(User=user)

    def searchUsers(self, args):
        fname = args.get("fname")
        lname = args.get("lname")
        uemail = args.get("uemail")
        uphone = args.get("uphone")

        dao = UserDAO()
        user_list = []
        if (len(args) == 2) and fname and lname:
            user_list = dao.getUserByFullName(fname, lname)
        elif (len(args) == 1) and fname:
            user_list = dao.getUserByFirstName(fname)
        elif (len(args) == 1) and lname:
            user_list = dao.getUserByLastName(lname)
        elif (len(args) == 1) and uemail:
            user_list = dao.getUserByEmail(uemail)
        elif (len(args) == 1) and uphone:
            user_list = dao.getUserByPhone(uphone)
        else:
            return jsonify(Error="Malformed query string"), 400

    def insertUser(self, form):
        print("form: ", form, 'len ', len(form.request))
        if len(form) != 2:
            return jsonify(Error="Malformed post request"), 400
        else:
            fname = form["fname"]
            lname = form["lname"]
            uemail = form["uemail"]
            uphone = form["uphone"]

            if fname and lname and uemail and uphone:
                dao = UserDAO()
                uid = dao.insert(fname, lname, uemail, uphone)
                result = self.build_user_attributes(
                    uid, fname, lname, uemail, uphone
                )
                return jsonify(User=result), 201
            else:
                return jsonify(Error="Unexpected attributes in post request"), 400

    def insertUserJson(self, json):
        if len(json) != 4: return jsonify(Error="Malformed Post request"), 400
        fname = json['fname']
        lname = json['lname']
        uemail = json['uemail']
        uphone = json['uphone']

        if fname and lname and uemail and uphone:
            dao = UserDAO()
            uid = dao.insert(fname, lname, uemail, uphone)
            result = self.build_user_attributes(uid, fname, lname, uemail, uphone)
            return jsonify(User=result), 201
        else:
            return jsonify(Error="Unexpected attributes in post request"), 400

    def deleteUser(self, uid):
        dao = UserDAO()
        if not dao.getUserById(uid):
            return jsonify(Error="Part not found."), 404
        else:
            dao.delete(uid)
            return jsonify(DeleteStatus="OK"), 200

    def updateUser(self, uid, json):
        dao = UserDAO()
        if not dao.getUserById(uid):
            return jsonify(Error="Part not found."), 404
        else:
            if len(json) != 4:
                return jsonify(Error="Malformed update request"), 400
            else:
                fname = json['fname']
                lname = json['lname']
                uemail = json['uemail']
                uphone = json['uphone']
                if fname and lname and uemail and uphone:
                    dao.update(uid, fname, lname, uemail, uphone)
                    result = self.build_user_attributes(uid, fname, lname, uemail, uphone)
                    return jsonify(User=result), 200
                else:
                    return jsonify(Error="Unexpected attributes in update request"), 400


