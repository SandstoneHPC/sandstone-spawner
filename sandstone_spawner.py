from jupyterhub.spawner import LocalProcessSpawner
from jupyterhub.utils import random_port

from traitlets import (
    Any, Bool, Dict, Instance, Integer, Float, List, Unicode,
    validate,
)

from subprocess import Popen
from tornado import gen
import pipes
import shutil
import os
import errno
import signal

SANDSTONE_HOME = os.environ.get('SANDSTONE_HOME')
APP_PATH = os.path.join(SANDSTONE_HOME, 'sandstone', 'app.py')
PYTHON_DIR = os.environ.get('PYTHON_DIR')
PYTHON_BIN = os.path.join(PYTHON_DIR, 'python')


class SandstoneSpawner(LocalProcessSpawner):
    TERM_TIMEOUT = Integer(5,
        help="""
        Seconds to wait for single-user server process to halt after SIGTERM.
        If the process does not exit cleanly after this many seconds of SIGTERM, a SIGKILL is sent.
        """
    ).tag(config=True)

    INTERRUPT_TIMEOUT = Integer(10,
        help="""
        Seconds to wait for single-user server process to halt after SIGINT.
        If the process has not exited cleanly after this many seconds, a SIGTERM is sent.
        """
    ).tag(config=True)

    KILL_TIMEOUT = Integer(5,
        help="""
        Seconds to wait for process to halt after SIGKILL before giving up.
        If the process does not exit cleanly after this many seconds of SIGKILL, it becomes a zombie
        process. The hub process will log a warning and then give up.
        """
    ).tag(config=True)

    @gen.coroutine
    def start(self):
        """Start the single-user server."""
        self.port = random_port()
        cmd = [PYTHON_BIN, APP_PATH]
        env = self.get_env()

        # cmd.extend(self.cmd)
        # cmd.extend('{}'.format(self.port))
        args = self.get_args()
        # print(args)
        cmd.extend(args)
        # import os
        # self.log.info(os.path.dirname(os.path.abspath(__file__)))

        self.log.info("Spawning %s", ' '.join(pipes.quote(s) for s in cmd))
        try:
            self.proc = Popen(cmd, env=env,
                preexec_fn=self.make_preexec_fn(self.user.name),
                start_new_session=True, # don't forward signals
            )
        except PermissionError:
            # use which to get abspath
            script = shutil.which(cmd[0]) or cmd[0]
            self.log.error("Permission denied trying to run %r. Does %s have access to this file?",
                script, self.user.name,
            )
            raise

        self.pid = self.proc.pid

        if self.__class__ is not LocalProcessSpawner:
            # subclasses may not pass through return value of super().start,
            # relying on deprecated 0.6 way of setting ip, port,
            # so keep a redundant copy here for now.
            # A deprecation warning will be shown if the subclass
            # does not return ip, port.
            if self.ip:
                self.user.server.ip = self.ip
            self.user.server.port = self.port
        return (self.ip or '127.0.0.1', self.port)

    @gen.coroutine
    def poll(self):
        """Poll the spawned process to see if it is still running.
        If the process is still running, we return None. If it is not running,
        we return the exit code of the process if we have access to it, or 0 otherwise.
        """
        # if we started the process, poll with Popen
        if self.proc is not None:
            status = self.proc.poll()
            if status is not None:
                # clear state if the process is done
                self.clear_state()
            return status

        # if we resumed from stored state,
        # we don't have the Popen handle anymore, so rely on self.pid
        if not self.pid:
            # no pid, not running
            self.clear_state()
            return 0

        # send signal 0 to check if PID exists
        # this doesn't work on Windows, but that's okay because we don't support Windows.
        alive = yield self._signal(0)
        if not alive:
            self.clear_state()
            return 0
        else:
            return None

    @gen.coroutine
    def _signal(self, sig):
        """Send given signal to a single-user server's process.
        Returns True if the process still exists, False otherwise.
        The hub process is assumed to have enough privileges to do this (e.g. root).
        """
        try:
            os.kill(self.pid, sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                return False  # process is gone
            else:
                raise
        return True  # process exists

    @gen.coroutine
    def stop(self, now=False):
        """Stop the single-user server process for the current user.
        If `now` is set to True, do not wait for the process to die.
        Otherwise, it'll wait.
        """
        if not now:
            status = yield self.poll()
            if status is not None:
                return
            self.log.debug("Interrupting %i", self.pid)
            yield self._signal(signal.SIGINT)
            yield self.wait_for_death(self.INTERRUPT_TIMEOUT)

        # clean shutdown failed, use TERM
        status = yield self.poll()
        if status is not None:
            return
        self.log.debug("Terminating %i", self.pid)
        yield self._signal(signal.SIGTERM)
        yield self.wait_for_death(self.TERM_TIMEOUT)

        # TERM failed, use KILL
        status = yield self.poll()
        if status is not None:
            return
        self.log.debug("Killing %i", self.pid)
        yield self._signal(signal.SIGKILL)
        yield self.wait_for_death(self.KILL_TIMEOUT)

        status = yield self.poll()
        if status is None:
            # it all failed, zombie process
            self.log.warning("Process %i never died", self.pid)
