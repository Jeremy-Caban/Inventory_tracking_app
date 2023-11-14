from app import app
from app.handlers.parts import PartHandler
from flask import Flask, jsonify, request

@app.route('/parts')
def getAllParts():
    if request.method == 'POST':
        print("REQUEST: ", request.json)
        return PartHandler().insertPart(request.form)
    else:
        if not request.args:
            return PartHandler().getAllParts()
        else:
            return PartHandler().searchParts(request.args)

@app.route('/parts/<int:pid>', methods=['GET', 'PUT', 'DELETE'])
def getPartById(pid):
    if request.method == 'GET':
        return PartHandler().getPartById(pid)
    elif request.method == 'PUT':
        return PartHandler().updatePart(pid, request.form)
    elif request.method == 'DELETE':
        return PartHandler().deletePart(pid)
    else:
        return jsonify(Error="Method not allowed."), 405    