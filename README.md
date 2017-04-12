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

### Spawn Jupyter Notebooks and Sandstone
If you would like JupyterHub to be able to spawn Sandstone as well as Jupyter Notebooks, configure the _ProfilesSpawner_ to wrap the _SandstoneSpawner_:
```python
c.JupyterHub.spawner_class = 'wrapspawner.ProfilesSpawner'
c.Spawner.http_timeout = 120

c.ProfilesSpawner.profiles = [( "Host process",
    'local','jupyterhub.spawner.LocalProcessSpawner', {'ip':'0.0.0.0'} ),
    ('Sandstone', 'sandstone','sandstone_spawner.spawner.SandstoneSpawner', {}),
]
```

## Running the Docker Image
The Docker image included in this repo provides an example setup of a JupyterHub instance that can spawn either a Jupyter Notebook or Sandstone instance. The image has two example users _(username:password)_:
* sandstone1:sandstone1
* sandstone2:sandstone2

To build and run this image:
```
docker build -t sandstone-jupyterhub .
docker run -p 8000:8000 -d sandstone-jupyterhub
```

JupyterHub will be accessible on http://localhost:8000/.
