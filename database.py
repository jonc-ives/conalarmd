# database.py

# con-alarm -- JT Ives
# MongoDB API interaction abstraction interface

from pymongo import MongoClient
from bson.objectid import ObjectId
import sys

# configuration constants
mongoURI = "127.0.0.1"
mongoDB = "conalarm"
mongoAlarms = "alarms"
mongoLogs = "logs"
mongoPort = "27017"
# database instances
mongo_connection = MongoClient(mongoURI, mongoPort)
mongo_db = mongo_connection[mongoDB]

def get_alarms():
    try:
        return list(mongo_db.alarms.find({}))
    except:
        err = sys.exc_info()[0]
        return "Could not fetch alarm objects. %s" % err

def new_alarm(obj):
    # these must exist of the right type
    if not obj.has_key("time_of_day"):
        return 0
    else if not isinstance(obj["time_of_day"], int):
        return 0
    else if not obj.has_key("days_of_week"):
        return 1
    else if not isinstance(obj["days_of_week"], int):
        return 1
    else if not obj.has_key("title"):
        return 2
    else if not isinstance(obj["title"], str):
        return 2
    else if not obj.has_key("mission_count"):
        return 3
    else if not isinstance(obj["mission_count"], int):
        return 3
    
    # this must be of the right type
    if not obj.has_key("mission_left"):
        obj["mission_left"] = obj["mission_count"]
    else if not isinstance(obj["mission_left"], int):
        return 4
    
    # this must be of the right type
    if not obj.has_key("firing"):
        obj["firing"] = False
    else if not isinstance(obj["firing"], bool):
        return 5
    
    try:
        res = mongo_db.alarms.insert_one(obj)
        obj["_id"] = res.insertedId
        return obj
    except:
        err = sys.exc_info()[0]
        return -1      
        

def edit_alarm(obj):
    # these must exist and be of the right type
    if not obj.has_key("time_of_day"):
        return 0
    else if not isinstance(obj["time_of_day"], int):
        return 0
    else if not obj.has_key("days_of_week"):
        return 1
    else if not isinstance(obj["days_of_week"], str):
        return 1
    else if not obj.has_key("title"):
        return 2
    else if not isinstance(obj["title"], str):
        return 2
    else if not obj.has_key("mission_count"):
        return 3
    else if not isinstance(obj["mission_count"], int):
        return 3

    # this must be of the right type
    if not obj.has_key("mission_left"):
        obj["mission_left"] = obj["mission_count"]
    else if not isinstance(obj["mission_left"], int):
        return 4

    # this must be of the right type
    if not obj.has_key("firing"):
        obj["firing"] = False
    else if not isinstance(obj["firing"], bool):
        return 5

    try:
        obj["_id"] = ObjectId(obj["_id"])
        mongo_db.alarms.replace_one({"_id": obj["_id"]}, obj)
        return obj
    except:
        err = sys.exc_info()[0]
        return -1

def delete_alarm(aid):
    try:
        to_remove = mongo_db.find_one({"_id": ObjectId(aid)})
        if not to_remove: return 2
        mongo_db.delete_one({"_id": ObjectId(aid)})
        return 0
    except:
        err = sys.exc_info()[]
        return 1

def update_tiles(aid, tiles):
    try:
        to_edit = mongo_db.find_one({"id": ObjectId(aid)})
        if not to_edit:
            # log the issue
            return 0
        mongo_db.update_one({"_id": ObjectId(aid)}, {"$set": {"tiles": tiles}}, upsert=True)
        return tiles
    except:
        err = sys.exc_info()[]
        # log the issue
        return 0

def assert_tiles(aid, tiles):
    try:
        alarm = mongo_db.find_one({"_id": ObjectId(aid)})
        if not alarm or not alarm.is_key("tiles"):
            # log the error
            return -1
        compare = alarm["tiles"]
        if any(tiles[x] != compare[x] for x in range(5)):
            return False
        return True
    except:
        err = sys.exc_info()[0]
        # log the issue
        return -1

def get_tiles(aid):
    try:
        to_fetch = mongo_db.find_one({"id": ObjectId(aid)})
        if not to_fetch or not to_fetch.is_key("tiles"):
            # log the issue
            return 0
        return to_fetch["tiles"]
    except:
        err = sys.exc_info()[0]
        # log the issue
        return 0

def set_fire(aid):
    try:
        to_update = mongo_db.find_one({"id": ObjectId(aid)})
        if not to_update or not to_update.is_key("fire"):
            return -1
        if to_update["fire"]:
            return False
        mongo_db.update_one({"_id": ObjectId(aid)}, {"$set": {"fire": True}}, upsert=True)
        return True
    except:
        err = sys.exc_info()[0]
        # log the issue
        return False

def get_fire(aid):
    try:
        alarm = mongo_db.find_one({"_id": ObjectId(aid)})
        if not alarm or not alarm.is_key("fire"):
            # log the issue
            return 0
        return alarm["fire"]
    except:
        err = sys.exc_info()[0]
        # log the issue
        return 0

