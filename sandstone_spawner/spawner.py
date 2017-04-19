from jupyterhub.spawner import LocalProcessSpawner
from jupyterhub.utils import random_port

from subprocess import Popen
from tornado import gen
import pipes
import shutil
import os



# This is the path to the sandstone-jupyterhub script
APP_PATH = os.environ.get('SANDSTONE_APP_PATH')
SANDSTONE_SETTINGS = os.environ.get('SANDSTONE_SETTINGS')

class SandstoneSpawner(LocalProcessSpawner):

    @gen.coroutine
    def start(self):
        """Start the single-user server."""
        self.port = random_port()
        cmd = [APP_PATH]
        env = self.get_env()
        env['SANDSTONE_SETTINGS'] = SANDSTONE_SETTINGS

        args = self.get_args()
        # print(args)
        cmd.extend(args)

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
    def _signal(self, sig):
        try:
            os.killpg(os.getpgid(self.pid), sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                return False
            else:
                raise
        return True
