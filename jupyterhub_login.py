from sandstone.lib.handlers.base import BaseHandler
import requests
import os

class JupyterHubLoginHandler(BaseHandler):
    def get(self):
        api_token = os.environ['JUPYTERHUB_API_TOKEN']

        url = '{protocol}://{host}/hub/api/authorizations/token/{token}'.format(
            protocol=self.request.protocol,
            host=self.request.host,
            token=api_token
        )

        res = requests.get(
            url,
            headers={
                'Authorization': 'token %s' % api_token
            }
        )


        username = res.json()['name']

        if username:
            self.set_secure_cookie('user', username)
            self.redirect('/user/{}'.format(username))
        else:
            self.set_status(403)
            self.redirect(self.get_login_url())
