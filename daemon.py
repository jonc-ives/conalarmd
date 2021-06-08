# daemon.py

# con-alarm -- JT Ives
# manages daemon process integration with kernel

import sys, os, time, atexit, signal

class daemon:
    """ a customize daemon class.

    Usage: subclass this daemon class and override the run() method."""

    def __init__(self, pidfile): self.pidfile = pidfile

    def daemonize(self):
        """Daemonize class. Employs UNIX double fork mechanism"""

        try:
            pid = os.fork()
            if pid > 0: sys.exit(0)
        except OSError as err:
            sys.stderr.write('primary fork failed: {0}\n'.format(err))
            sys.exit(1)

        # decouple from parent env
        os.chdir('/')
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0: sys.exit(0)
        except OSError as err:
            sys.stderr.write('redundant fork failed: {0}\n'.format(err))
            sys.exit(1)

        # redirect std file desc.
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as pf:
            pf.write(pid + '\n')

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """ start the daemon """

        try: # check for runstate with pidfile
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = "pidfile {0} already exists. Daemon already running?\n"
            sys.stderr.write(message.format(self.pidfile))
            sys.exit(1)

        # start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """ stop the daemon """

        try: # check for runstate with pidfile
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = "pidfile {0} does not exist. Daemon not running?\n"
            sys.stderr.write(message.format(self.pidfile))
            return # usually happens in restarts -- not an error
        
        try: # try killing daemon process
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err.args))
                sys.exit(1)

        def restart(self):
            """ Restart the daemon. """
            self.stop()
            self.start()

        def run(self):
            """ This needs to be overridden when Daemon is subclasses

            It will only be called after the process is daemonized by start() or restart()"""
            pass
        






