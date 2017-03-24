#!/bin/bash

source /home/saurabh/workspace/jupyterhub-tornado/sandstone-ide/venv/bin/activate
/home/saurabh/workspace/jupyterhub-tornado//sandstone-ide/venv/bin/python /home/saurabh/workspace/jupyterhub-tornado//sandstone-ide/sandstone/app.py "$@"
