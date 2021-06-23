# database.py

# con-alarm -- JT Ives
# MongoDB API interaction abstraction interface

import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from globals import *
import sys

# activate file-level logger
log = logging.getLogger(__name__)

# configuration constants
mongoURI = "127.0.0.1"
mongoDB = "conalarm"
mongoAlarms = "alarms"
mongoLogs = "logs"
mongoPort = 27017

# database instances
mongo_connection = MongoClient(mongoURI, mongoPort)
mongo_db = mongo_connection[mongoDB]

def get_alarms(aid=""):
    """ Fetches alarm objects. Fetches one with param aid passed. Returns
    list(alarms) or error code. """
    
    try:
        if aid == "":
            alarms = list(mongo_db.alarms.find({}))
            if not alarms: log.warning("Could not locate any alarm objects from mongo store...")
        else:
            alarms = list(mongo_db.alarms.find_one({"_id": ObjectId(aid)}))
            if not alarms:
                log.exception("Could not fetch alarm object. Unmatched aid AID[%s]" % aid)
                return MISSING_ALARM
        return alarms
    except:
        log.exception("Failed to fetch alarm objects AID[%s]" % (aid if aid != "" else "ALL"))
        return DATABASE_ERROR

def get_alarm_prop(aid, prop):
    """ Fetches alarm property. Returns (<bool>success, value) on success.
    Returns (<bool>success, error_code) on failure. Flag to prevent contamination
    between error codes and int value returns. """

    try:
        alarm = mongo_db.alarms.find_one({"_id": ObjectId(aid)})
        if not alarm: raise TypeError
        if not alarm.get(prop): raise KeyError
        return alarm[prop]
    except TypeError:
        log.exception("Failed to fetch alarm property '%s'. Missing alarm object AID[%s]" % prop, aid)
        return MISSING_ALARM
    except KeyError:
        log.exception("Failed to fetch alarm property '%s'. Missing propery '%s' AID[%s]" % prop, prop, aid)
        return MISSING_ALARM_PROP
    except:
        log.exception("Failed to fetch alarm property '%s' AID[%s]" % (prop, aid))
        return DATABASE_ERROR
        
def new_alarm(obj):
    """ Validates and creates alarm object from parameter obj. Returns
    error code or newly created alarm object. """

    obj = validate_alarm(obj)
    if isinstance(obj, int):
        return obj

    try:
        res = mongo_db.alarms.insert_one(obj)
        obj["_id"] = res.inserted_id
        return obj
    except:
        log.exception("Could not create new alarm object")
        return DATABASE_ERROR
        
def edit_alarm(obj):
    """ Validates and edits alarm object from parameter obj. Returns
    error code or edited alarm object. """

    obj = validate_alarm(obj)
    if isinstance(obj, int):
        return obj

    try:
        obj["_id"] = ObjectId(obj["_id"])
        to_edit = mongo_db.alarms.find_one({"_id": obj["_id"]})
        if not to_edit:
            log.exception("Could not edit alarm object. Alarm object not found AID[%s]" % str(obj["_id"]))
            return MISSING_ALARM
        mongo_db.alarms.replace_one({"_id": obj["_id"]}, obj)
        return obj
    except:
        log.exception("Could not edit alarm object AID[%s]" % ObjectId(obj["_id"]))
        return DATABASE_ERROR

def edit_alarm_prop(aid, prop, value):
    """ Validates prop value pair. Edits database alarm object. Returns
    adjusted object on success. Returns error code on failure. """

def delete_alarm(aid):
    """ Deletes alarm from database. Returns operation code. """

    try:
        to_remove = mongo_db.alarms.find_one({"_id": ObjectId(aid)})
        if not to_remove:
            log.exception("Failed to remove alarm object. Alarm object not AID[%s]" % aid)
            return MISSING_ALARM
        mongo_db.alarms.delete_one({"_id": ObjectId(aid)})
        return OP_SUCCESS
    except:
        log.exception("Failed to remove alarm AID[%s]" % aid)
        return DATABASE_ERROR

def validate_alarm(obj):
    """ validates alarm object for database operations. Returns error code on failure.
    Returns corrected (when applicable) object on success. IMPORTANT: when props mission_left
    or firing are not set, will be set to defaults. """

    if not isinstance(obj, dict):
        return INVALID_OBJECT

    # these must exist of the right type
    if not obj.get("time_of_day"):
        return MISSING_TOD
    elif not isinstance(obj["time_of_day"], int):
        return INVALID_TOD
    elif not obj.get("days_of_week"):
        return MISSING_DOW
    elif not isinstance(obj["days_of_week"], int):
        return INVALID_DOW
    elif not obj.get("title"):
        return MISSING_TITLE
    elif not isinstance(obj["title"], str):
        return INVALID_TITLE
    elif not obj.get("mission_count"):
        return MISSING_MISSION_CNT
    elif not isinstance(obj["mission_count"], int):
        return INVALID_MISSION_CNT
    
    # this must be of the right type
    if not obj.get("mission_left"):
        obj["mission_left"] = obj["mission_count"]
    elif not isinstance(obj["mission_left"], int):
        return INVALID_MISSION_LFT
    
    # this must be of the right type
    if not obj.get("firing"):
        obj["firing"] = False
    elif not isinstance(obj["firing"], bool):
        return INVALID_FIRING

    return obj

def validate_prop(prop, value):
    """ validates a property value pair for mongo store query updates.
    Returns OP_SUCCESS flag on success. Error code on failure. """

    if prop == "time_of_day":
        return OP_SUCCESS if value in range(1, 60*60*24) else INVALID_TOD
    elif prop == "days_of_week":
        return OP_SUCCESS if value in range(0, 2^6) else INVALID_DOW
    elif prop == "title":
        return OP_SUCCESS if isinstance(value, str) else INVALID_TITLE
    elif prop == "mission_count":
        return OP_SUCCESS if value in range(0, 20) else INVALID_MISSION_CNT
    elif prop == "mission_left":
        return OP_SUCCESS if value in range(0, 20) else INVALID_MISSION_LFT
    elif prop == "firing":
        return OP_SUCCESS if isinstance(value, bool) else INVALID_FIRING
    return INVALID_PROPERTY

# def update_tiles(aid, tiles):
#     """ Updates alarm property tiles. Returns (tiles, mission_left), else (error code, 0) """

#     try:
#         to_edit = mongo_db.alarms.find_one({"id": ObjectId(aid)})
#         if not to_edit: raise TypeError
#         mongo_db.update_one({"_id": ObjectId(aid)}, {"$set": {"tiles": tiles}}, upsert=True)
#         return get_tiles(aid)
#     except TypeError:
#         log.exception("Failed to update alarm property 'tiles'. Missing alarm object AID[%s]" % aid)
#         return MISSING_ALARM, 0
#     except:
#         log.exception("Failed to update alarm property 'tiles' AID[%s]" % aid)
#         return DATABASE_ERROR, 0

# def assert_tiles(aid, tiles):
#     """ Checks to see if param 'tiles' matches with alarm's tiles. Updates alarm
#     mission_left property on success, as well as firing when applicable. Returns
#     bool indicating result, or error code. """

#     try:
#         alarm = mongo_db.find_one({"_id": ObjectId(aid)})
#         if not alarm: raise TypeError
#         compare = alarm["tiles"]
#         if any(tiles[x] != compare[x] for x in range(5)):
#             return False

#         # update alarm object to reflect success
#         alarm["mission_left"] -= 1
#         if alarm["mission_left"] == 0:
#             alarm["mission_left"] = alarm["mission_count"]
#             alarm["tiles"] = [-1, -1, -1, -1, -1]
#             alarm["firing"] = False
#         # save the changes to the database
#         alarm = edit_alarm(alarm)
#         if not isinstance(alarm, dict):
#             raise RuntimeError
#         return True
#     except TypeError:
#         log.exception("Failed to assert alarm tiles. Missing alarm object AID[%s]" % aid)
#         return MISSING_ALARM
#     except RuntimeError:
#         log.exception("Assertion successful. Failed to update alarm AID[%s]" % aid)
#         return DATABASE_ERROR
#     except:
#         log.exception("Failed to assert alarm tiles AID[aid]")
#         return DATABASE_ERROR

# def get_tiles(aid):
#     """ Returns (tiles, mission_left) or throws RunTime """

#     try:
#         to_fetch = mongo_db.find_one({"id": ObjectId(aid)})
#         if not to_fetch: raise TypeError
#         elif not to_fetch.is_key("tiles") or not to_fetch.is_key("mission_left"):
#             missing = to_fetch.is_key("tiles") ? "mission_left" : "tiles" 
#             raise KeyError
#         return to_fetch["tiles"], to_fetch["mission_left"]
#     except TypeError:
#         log.exception("Failed to fetch alarm property 'tiles'. Missing alarm object AID[%s]" % aid)
#         raise RuntimeError
#     except KeyError:
#         log.exception("Failed to fetch alarm property 'tiles'. Missing property '%s' AID[%s]" % aid, missing)
#         raise RuntimeError
#     except:
#         log.exception("Failed to fetch alarm property 'tiles' AID[%s]" % aid)
#         raise RuntimeError

# def set_fire(aid):
#     """ Sets alarm 'fire' property. Throws on failure. """

    #     try:
    #         to_update = mongo_db.find_one({"id": ObjectId(aid)})
    #         if not to_update: raise TypeError
    #         mongo_db.update_one({"_id": ObjectId(aid)}, {"$set": {"fire": True}}, upsert=True)
    #         return OP_SUCCESS
    #     except TypeError:
    #         log.exception("Failed to fetch alarm property 'firing'. Missing alarm object AID[%s]" % aid)
    #         raise Exception
    #     except:
    #         log.exception("Failed to fetch alarm property AID[%s]" % aid)
    #         raise Exception

# def get_fire(aid):
#     """ Returns alarm 'fire' property. Throws on failure. """

        # try:
        #     alarm = mongo_db.find_one({"_id": ObjectId(aid)})
        #     if not alarm: raise TypeError
        #     if not alarm.is_key("fire"): raise KeyError
        #     return alarm["fire"]
        # except TypeError:
        #     log.exception("Failed to fetch alarm property 'firing'. Missing alarm object AID[%s]" % aid)
        #     raise Exception
        # except KeyError:
        #     log.exception("Failed to fetch alarm property 'firing'. Missing property 'firing' AID[%s]" % aid)
        #     raise Exception
        # except:
        #     log.exception("Failed to fetch alarm propery 'firing' AID[%s]" % aid)
        #     raise Exception
