# server.py

# con-alarm -- JT Ives
# flask (+RESTful) server endpoints for web-app controls

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import numpy

class AlarmInfo(Resource):

    def get(self):
        alarms = database.get_alarms()
        if not isinstance(alarms, object):
            return 500, jsonify({"msg": alarms, "firing": False})

        if any(a["firing"] == True for a in alarms):
            a["_id"] = str(a["_id"])
            return jsonify({"alarms": a, "firing": True})
        
        for a in alarms: a["_id"] = str(a["_id"])
        return jsonify({"firing": False, "alarms": alarms})

    def post(self):
        args = request.get_json(force=True)
        alarm = database.new_alarm(args)
        if not isinstance(alarm, object):
            if alarm == -1: return 500, jsonify({"msg": "Failed to create alarm."})
            else: return 400, jsonify({"msg": "Invalid request [PROPERR] Field #{0}".format(alarm)})
        alarm["_id"] = str(alarm["_id"])
        return jsonify({"new": alarm, "msg": "Alarm successfully created."})

class AlarmActions(Resource):

    def post(self, aid):
        args = request.get_json(force=True)
        alarm = database.edit_alarm(args)
        if not isinstance(alarm, object):
            if alarm == -1: return 500, jsonify({"msg": "Failed to edit alarm."})
            else: return 400, jsonify({"msg": "Invalid request [PROPERR] Field #{0}".format(alarm)})
        alarm["_id"] = str(alarm["_id"])
        return jsonify({"edited": alarm, "msg": "Message successfully created."})

    def delete(self, aid):
        ret_code = database.delete_alarm(aid)
        if ret_code == 0: return jsonify("msg": "Alarm successfully created.")
        if ret_code == 1: return 500, jsonify("msg": "Failed to delete alarm.")
        if ret_code == 2: return 400, jsonify("msg": "Could not locate indicated alarm.")
        
class AlarmHandler(Resource):

    def get(self, aid):
        tiles = numpy.random.randint(0, 25, 5)
        tiles = database.update_tiles(aid, tiles)
        if not isinstance(tiles, list):
            return 500, jsonify({"msg": "Failed to update tiles. See application log file for more information."})
        return jsonify({"tiles": tiles})

    def post(self, aid):
        args = request.get_json(force=True)
        attempt = args["titles"]
        correct, count = database.get_tiles(aid)
        if not isinstance(correct, list):
            if correct == 1: return 500, jsonify({"msg": "Failed to test tile accuracy."})
            else: return 400, jsonfiy({"msg": "Invalid request [QUERYERR]"})
        if any(attempt[i] != correct[i] for i in range(5)):
            return jsonify({"success": False, "count": count})
        return jsonfiy({"success": True, "count": count})

class APIManager:

    def __init__(init):
        self.app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath("application.py")))
        self.api = Api(app)

        @app.route('/', methods=['GET'])
        def Index(): # index endpoint (simple flask)
            return render_template("index.html")

        self.api.add_resource(AlarmInfo, '/alarms')
        self.api.add_resource(AlarmActions, '/alarm/<aid>')
        self.api.add_resource(AlarmHandler, '/handle/<aid>')

