# application.py

# con-alarm -- JT Ives
# manages application logic

import sys, time, os, database
from datetime import datetime
from daemon import Daemon
from server import APIManager
from playsound import playsound

# activate file-level logger
from logger import root as log

class Session(Daemon):
    """ Subclasses Daemon from daemon.py. Manages application logic. """
    
    def run(self):
        """ Overrides parent. Only called after process is daemonized. 
        Manages the applications session. """

        moment = (now_day * 24 * 60 * 60) + now_seconds
        # adjust for alarm next week
        if moment > fires + 10: fires += (7 * 24 * 60 * 60)
        # now we can calculate the interval
        temp = abs(fires - moment)
        # store the decision
        seconds_til = min(seconds_til, temp)
        
        return False if seconds_til > 3 else True


    def initialize_managers(self):
        """ Reads application configuration to initialize alarm managers. """
        pass

def manage_active_alarm(aid):
    """ If alarm.fire is unset, sets property and fires alarm. """

    try:
        if not database.get_alarm_prop(aid, "firing"):
            database.edit_alarm_prop(aid, "firing", True)
            pid = os.fork()
            if pid != 0: return
            fire_alarm(aid)
    except: log.exception("Failed to initialize alarm sequence AID[%s]" % aid)

def fire_alarm(aid):
    """ Fires and manages alarm. Terminates process on completion.
    Must act as child. """

    while True:
        playsound('alarm.wav')
        if not database.get_alarm_prop(aid, "fire"):
            exit(0)
    
if __name__ == "__main__":
    app = Session('/tmp/conalarm.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]: app.start()
        elif 'stop' == sys.argv[1]: app.stop()
        elif 'restart' == sys.argv[1]: app.restart()
    else: print("usage: %s start|stop|restart" % sys.argv[0])
