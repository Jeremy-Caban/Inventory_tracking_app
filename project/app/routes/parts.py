from app import app
from app.handlers.parts import PartHandler
@app.route('/parts')
def getAllParts():
    return PartHandler().getAllParts()
