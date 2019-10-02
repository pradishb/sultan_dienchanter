''' Moudule for league client communication '''
import os

import lcu_connector_python as lcu
import requests

from settings import RIOT_CLIENT_CONFIG


class ClientConnectionException(Exception):
    ''' Raised when there is error when connecting to league client '''


class Connection:
    ''' Connects to league client and communicates with it '''

    def __init__(self):
        self.kwargs = None
        self.url = None

    def get_connection(self):
        ''' Parses connection url and port from lockfile '''
        connection = lcu.connect(os.path.expanduser(RIOT_CLIENT_CONFIG))
        if connection == 'Ensure the client is running and that you supplied the correct path':
            raise ClientConnectionException
        self.kwargs = {
            'verify': False,
            'auth': ('riot', connection['authorization']),
            'timeout': 30
        }
        self.url = 'https://' + connection['url']

    def get(self, url, *args, **kwargs):
        ''' Wrapper around requests get method '''
        self.get_connection()
        return requests.get('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def post(self, url, *args, **kwargs):
        ''' Wrapper around requests post method '''
        self.get_connection()
        return requests.post('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def patch(self, url, *args, **kwargs):
        ''' Wrapper around requests patch method '''
        self.get_connection()
        return requests.patch('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def put(self, url, *args, **kwargs):
        ''' Wrapper around requests put method '''
        self.get_connection()
        return requests.put('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)
