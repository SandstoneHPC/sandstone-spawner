from jupyterhub.spawner import LocalProcessSpawner
from jupyterhub.traitlets import Command
from traitlets import (
    Integer, Unicode, Float, Dict, List, Bool, default
)
from tornado import gen
import os


class SandstoneSpawner(LocalProcessSpawner):
    """SandstoneSpawner - extends the default LocalProcessSpawner to allow JupyterHub to
    spawn and manage Sandstone servers alongside notebook servers. This spawner can be
    configured for JupyterHub running as an unprivileged user with sudo permissions to
    the sandstone-jupyterhub command.
    """
    sandstone_cmd = Command(['sandstone-jupyterhub'],
        help="""
        This is the path to the sandstone-jupyterhub executable that the spawner
        will call to start a JupyterHub-compatible user server.
        """
    ).tag(config=True)

    sandstone_settings = Unicode('',
        help="""
        This is the absolute path to the settings module that should be imported by each
        spawned Sandstone server. The SANDSTONE_SETTINGS environment variable will not be
        set if this value is empty.
        """
    ).tag(config=True)

    setuid_enabled = Bool(True,
        help="""
        Whether or not SandstoneSpawner should use setuid when spawning Sandstone servers. If
        set to True (default), the spawner will function like LocalProcessSpawner. If set to
        False, then SandstoneSpawner will skip the setuid step and instead use sudo -u <username>
        to start the sandstone-jupyterhub command. Your sudoers file must be configured to permit
        the JupyterHub user to use sudo for the sandstone-jupyterhub command in this configuration.
        """
    ).tag(config=True)

    def make_preexec_fn(self, name):
        """
        If the setuid_enabled is set to False, then this method skips the set_user_setuid call
        and return None.
        """
        if self.setuid_enabled:
            return super().make_preexec_fn(name)
        return None

    def get_env(self):
        """
        Extends get_env to set the SANDSTONE_SETTINGS variable in the spawned process environment
        """
        env = super().get_env()
        if self.sandstone_settings:
            env['SANDSTONE_SETTINGS'] = self.sandstone_settings
        return env

    @property
    def cmd(self):
        cmd = []
        if not self.setuid_enabled:
            sudo_cmd = 'sudo -u {username}'.format(username=self.user.name)
            cmd.append(sudo_cmd)
        cmd.extend(self.sandstone_cmd)
        return cmd

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
