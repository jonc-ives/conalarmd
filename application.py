# application.py

# con-alarm -- JT Ives
# manages application logic

import logger, logging
import sys, time, os, database
from daemon import Daemon
from server import APIManager
from playsound import playsound

# activate file-level logger
log = logging.getLogger(__name__)

class Session(Daemon):
    """ Subclasses Daemon from daemon.py. Manages application logic. """
    
    def run(self):
        """ Overrides parent. Only called after process is daemonized. 
        Manages the applications session. """

        api = APIManager()
        api.app.run(host='0.0.0.0')
        # configures external alarm handlers
        self.initialize_managers()
        # begin the application session
        while 1: # session loop
            time.sleep(60)
            # update alarm list
            alarms = database.get_alarms()
            # prevents key errors
            if not isinstance(alarms, list):
                log.exception("Requested alarms is not a list of objects")
            # manage any firing alarms
            elif any(self.is_firing(a["time_of_day"], a["days_of_week"]) for a in alarms):
                manage_active_alarm(a["_id"])           

    def is_firing(self, tod, dow):
        """ Determines if an alarm should be fired. Returns bool. """
        pass

    def initialize_managers(self):
        """ Reads application configuration to initialize alarm managers. """
        pass

def manage_active_alarm(aid):
    """ If alarm.fire is unset, sets property and fires alarm. """

        try:
            if not database.get_fire(aid):
                database.set_fire(aid)
                pid = os.fork()
                if pid != 0: return
                fire_alarm(aid)
        except: log.exception("Failed to initialize alarm sequence AID[%s]" % aid)

def fire_alarm(aid):
    """ Fires and manages alarm. Terminates process on completion.
    Must act as child. """

    while True:
        playsound('alarm.wav')
        if not database.get_fire(aid):
            exit(0)
    
if __name__ == "__main__":
    app = Session('/tmp/conalarm.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]: app.start()
        elif 'stop' == sys.argv[1]: app.stop()
        elif 'restart' == sys.argv[1]: app.restart()
    else: print "usage: %s start|stop|restart" % sys.argv[0]
