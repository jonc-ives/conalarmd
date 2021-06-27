# server.py

# con-alarm -- JT Ives
# flask (+RESTful) server endpoints for web-app controls

from flask import Flask, jsonify, render_template, request
from flask_restful import Resource, Api
import database, numpy, os
from globals import *

# activate file-level logger
from logger import root as log

class AlarmInfo(Resource):

    def get(self):
        """ Prepares and sends alarm objects to client. Returns {"error":..}, {"firing": <obj>alarm},
        {"alarms": [<obj>]alarm}, depending on mongo store fetch results. """

        alarms = database.get_alarms()
        if alarms == DATABASE_ERROR:
            return jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"})
  
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
                return jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"})
            else: return jsonify({"error": "Oops! It looks like there was a problem with your request ERR[%s]" % alarm})
        
        alarm["_id"] = str(alarm["_id"])
        return jsonify({"new": alarm, "msg": "Alarm successfully created."})

class AlarmActions(Resource):

    def post(self, aid):
        """ Handles requests for editing alarm objects. Returns {"error":..}, {"edited", <obj>alarm, "msg":..} """

        args = request.get_json(force=True)
        alarm = database.edit_alarm(args)

        if isinstance(alarm, int):
            if alarm == DATABASE_ERROR:
                return jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"})
            else: return jsonify({"error": "Oops! It looks like there was a problem with your request ERR[%s]" % alarm})

        alarm["_id"] = str(alarm["_id"])
        return jsonify({"edited": alarm, "msg": "Alarm successfully edited."})

    def delete(self, aid):
        """ Handles requests to delete alarm objects from the mongo store. Returns {"error":..}, {"msg":..} """

        ret_code = database.delete_alarm(aid)
        
        if ret_code == DATABASE_ERROR:
            return jsonify({"error": "Uh oh! The application encountered some errors. Try again in a few minutes"})
        elif ret_code == MISSING_ALARM:
            return jsonify({"error": "Nope. That alarm doesn't exist. Try refreshing the page..."})
        elif ret_code == OP_SUCCESS:
            return jsonify({"msg": "Alarm successfully removed."})

        return jsonify({"error": "Huh. We're currently encountering some corner-case server errors. Please try again later."})
     
class AlarmHandler(Resource):

    def post(self, aid):
        """ Terminates alarm with _id 'aid'. Returns {"msg":..}, {"error":..} """

        args = request.get_json(force=True)
        if args.get("complete"):
            alarm = database.edit_alarm_prop(aid, "firing", False)
            if isinstance(alarm, int):
                return jsonify({"error": "Uh oh! The application ran into some errors ERR[%s]" % alarm})
            return jsonify({"msg": "Alarm successfully terminated"})
        
        return jsonify({"error": "Whoops! Request is missing paramater 'tiles' [<int>]"})

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

