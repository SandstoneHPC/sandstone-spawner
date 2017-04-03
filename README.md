# sandstone-spawner
JupyterHub Spawner class for starting Sandstone HPC user instances

## Setup instructions
* Clone the repository. `git clone https://github.com/ResearchComputing/sandstone-spawner.git`
* Create a new virtualenv for **Python 3**. and activate it
* Install the requirements: `pip install -r requirements.txt`
* Set the `SANDSTONE_HOME` environment variable to the fully qualified path where sandstone is located.
* Set the `PYTHON_DIR` environment variable to the path of the **Python 2 interpreter used by Sandstone**. This could be the path to the `bin` directory of the virtualenv used by Sandstone.
* Run jupyterhub with the `jupyterhub` command.
* Signing in will start a Sandstone instance

## The `jupyterhub_config` file
The `jupyterhub_config` file is modified to set the default spawner as `SandstoneSpawner`.

The following line sets the spawner as `SandstoneSpawner`

`c.JupyterHub.spawner_class = 'sandstone_spawner.SandstoneSpawner'`

Other JupyterHub parameters can also be configured in the `jupyterhub_config` file.
