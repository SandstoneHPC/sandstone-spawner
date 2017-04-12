FROM ubuntu:16.04
RUN ln -sf /bin/bash /bin/sh
MAINTAINER Zebula Sampedro <sampedro@colorado.edu>

# Installs
RUN apt-get update && apt-get install -y build-essential \
    python-dev python-pip virtualenv \
    nodejs nodejs-legacy npm \
    python-yaml \
    git
RUN npm install -g npm@2
RUN npm install -g configurable-http-proxy

# Add user
RUN useradd -m sandstone1
RUN echo "sandstone1:sandstone1" | chpasswd

# Add another user
RUN useradd -m sandstone2
RUN echo "sandstone2:sandstone2" | chpasswd

# clone required repos
RUN mkdir -p /home/sandstone/
WORKDIR /home/sandstone
RUN git clone https://github.com/SandstoneHPC/sandstone-ide.git
RUN git clone https://github.com/SandstoneHPC/sandstone-jupyterhub-login.git
RUN git clone https://github.com/jupyterhub/wrapspawner.git
RUN git clone https://github.com/SandstoneHPC/sandstone-spawner.git

WORKDIR /home/sandstone
RUN virtualenv -p $(which python) sandstone-venv && \
    source sandstone-venv/bin/activate && \
    cd sandstone-ide && \
    pip install -r requirements.txt && \
    cd sandstone/client && \
    npm install && \
    node_modules/bower/bin/bower install --allow-root && \
    cd ../../ && \
    python setup.py install && \
    cd ../sandstone-jupyterhub-login && \
    python setup.py install

WORKDIR /home/sandstone
RUN virtualenv -p $(which python3.5) jh-venv
RUN source jh-venv/bin/activate && \
    pip install jupyterhub && \
    cd sandstone-spawner && \
    python setup.py install && \
    cd ../wrapspawner && \
    python setup.py install && \
    pip install jupyter
ENV JH_BIN=/home/sandstone/jh-venv/bin/jupyterhub

#Jupyterhub configuration
ENV JUPYTERHUB_CONFIG=/home/sandstone/jupyterhub_config.py
RUN echo "c.JupyterHub.spawner_class = 'wrapspawner.ProfilesSpawner'" > $JUPYTERHUB_CONFIG
RUN echo "c.Spawner.http_timeout = 120" >> $JUPYTERHUB_CONFIG
RUN echo "c.ProfilesSpawner.profiles = [( 'Jupyter Notebook', 'local', 'jupyterhub.spawner.LocalProcessSpawner',{'ip':'0.0.0.0'} ),('Sandstone', 'sandstone','sandstone_spawner.spawner.SandstoneSpawner', {}),]" >> $JUPYTERHUB_CONFIG

ENV PATH=$PATH:/home/sandstone/jh-env/bin
ENV SANDSTONE_APP_PATH=/home/sandstone/sandstone-venv/bin/sandstone-jupyterhub
EXPOSE 8000

LABEL org.jupyter.service="jupyterhub"

# Sandstone configuration
RUN mkdir -p /home/sandstone/.config/sandstone/
ENV SANDSTONE_CONFIG=/home/sandstone/.config/sandstone/sandstone_settings.py
#ADD sandstone_settings.py /home/sandstone/.config/sandstone/
RUN echo "import os" > $SANDSTONE_CONFIG
RUN echo "INSTALLED_APPS=('sandstone.lib', 'sandstone.apps.codeeditor', 'sandstone.apps.filebrowser', 'sandstone.apps.webterminal',)" >> $SANDSTONE_CONFIG
RUN echo "URL_PREFIX=os.environ.get('SANDSTONE_PREFIX', '')"
RUN echo "LOGIN_HANDLER='sandstone_jupyterhub_login.handlers.JupyterHubLoginHandler'" >> $SANDSTONE_CONFIG
ENV SANDSTONE_SETTINGS=/home/sandstone/.config/sandstone/sandstone_settings.py

RUN cp /home/sandstone/jh-venv/bin/jupyterhub-singleuser /usr/bin
CMD ["/bin/bash", "-c", "$JH_BIN", "--config", "$JUPYTERHUB_CONFIG"]
