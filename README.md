# sandstone-spawner
JupyterHub Spawner class for starting Sandstone HPC user instances

## Installation
**This module requires the JupyterHub Login Handler for Sandstone, found at https://github.com/SandstoneHPC/sandstone-jupyterhub-login**

Install the module with
```
python setup.py install
```

Set the `SANDSTONE_APP_PATH` environment variable to the absolute path of the `sandstone-jupyterhub` executable. This executable is provided by `sandstone-jupyterhub-login`.
```
export SANDSTONE_APP_PATH=/path/to/sandstone-jupyterhub
```

## JupyterHub Config
Modify your JupyterHub config file to set the default spawner as `SandstoneSpawner`.
```python
c.JupyterHub.spawner_class = 'sandstone_spawner.spawner.SandstoneSpawner'
```
