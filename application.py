# application.py

# con-alarm -- JT Ives
# manages application logic

import sys, time, os, database
from daemon import Daemon
from server import ApiManager
from playsound import playsound

class Session(Daemon):
    """ Subclasses Daemon from daemon.py

    Manages application logic """
    
    def run(self):
        api = ApiManager()
        api.app.run()

        while 1: # session loop
            time.sleep(60)
            # update alarm list
            alarms = database.get_alarms()
            if not isinstance(alarms, object):
                # log the issue
                continue
            # manage any firing alarms
            if any(self.is_firing(a["time_of_day"], a["days_of_week"]) for a in alarms):
                manage_active_alarm(a["_id"])           

    def is_firing(self, tod, dow):
        pass

def manage_active_alarm(aid):
    if database.set_fire(aid):
        pid = os.fork()
        if pid > 0: return
        play_alarm(aid)

def play_alarm(aid):
    while True:
        playsound('alarm.wav')
        if not database.get_fire(aid):
            exit(0)
    
if __name__ == "__main__":
    app = Session('/tmp/conalarm.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            app.start()
        elif 'stop' == sys.argv[1]:
            app.stop()
        elif 'restart' == sys.argv[1]:
            app.restart()
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(0)
