# server.py

# con-alarm -- JT Ives
# flask (+RESTful) server endpoints for web-app controls

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import database, numpy, logging, os
from globals import *

# activate file-level logger
log = logging.getLogger(__name__)

class AlarmInfo(Resource):

    def get(self):
        """ Prepares and sends alarm objects to client. Returns {"error":..}, {"firing": <obj>alarm},
        {"alarms": [<obj>]alarm}, depending on mongo store fetch results. """

        alarms = database.get_alarms()
        if alarms == DATABASE_ERROR:
            return jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"}), 500
  
        if any(a["firing"] for a in alarms):
            a["_id"] = str(a["_id"])
            return jsonify({"firing": a})
        
        for a in alarms: a["_id"] = str(a["_id"])
        return jsonify({"alarms": alarms})

    def post(self):
        """ Handles requests for new alarm objects. Returns {"error":..}, {"new": <obj>alarm, "msg":..} """

        args = request.get_json(force=True)
        alarm = database.new_alarm(args)

        if isinstance(alarm, int):
            if alarm == DATABASE_ERROR:
                return 500, jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"})
            else: return 400, jsonify({"error": "Oops! It looks like there was a problem with your request ERR[%s]" % alarm})
        
        alarm["_id"] = str(alarm["_id"])
        return jsonify({"new": alarm, "msg": "Alarm successfully created."})

class AlarmActions(Resource):

    def post(self, aid):
        """ Handles requests for editing alarm objects. Returns {"error":..}, {"edited", <obj>alarm, "msg":..} """

        args = request.get_json(force=True)
        alarm = database.edit_alarm(args)

        if isinstance(alarm, int):
            if alarm == DATABASE_ERROR:
                return 500, jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"})
            else: return jsonify({"error": "Oops! It looks like there was a problem with your request ERR[%s]" % alarm})

        alarm["_id"] = str(alarm["_id"])
        return jsonify({"edited": alarm, "msg": "Alarm successfully edited."})

    def delete(self, aid):
        """ Handles requests to delete alarm objects from the mongo store. Returns {"error":..}, {"msg":..} """

        ret_code = database.delete_alarm(aid)
        
        if ret_code == DATABASE_ERROR:
            return 500, jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"})
        elif ret_code == MISSING_ALARM:
            return 400, jsonify({"error": "Nope. That alarm doesn't exist. Try refreshing the page..."})
        elif ret_code == OP_SUCCESS:
            return jsonify({"msg": "Alarm successfully removed."})

        return 500, jsonify({"error": "Huh. We're currently encountering some corner-case server errors. Please try again later."})
     
class AlarmHandler(Resource):

    def get(self, aid):
        tiles = numpy.random.randint(0, 25, 5)

    def post(self, aid):
        args = request.get_json(force=True)


class APIManager:

    def __init__(self):
        self.app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath("application.py")))
        self.api = Api(self.app)

        @self.app.route('/', methods=['GET'])
        def Index(): # index endpoint (simple flask)
            return render_template("index.html")

        self.api.add_resource(AlarmInfo, '/alarms')
        self.api.add_resource(AlarmActions, '/alarm/<aid>')
        self.api.add_resource(AlarmHandler, '/handle/<aid>')

