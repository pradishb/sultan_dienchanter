import time
import logging

from connection.riot import Connection
from .exceptions import ConsentRequiredException, AuthenticationFailureException


class RiotClient:
    def __init__(self):
        self.state = None
        self.connection = Connection()

    def update(self):
        res = self.connection.get('/rso-auth/v1/authorization')
        if res.status_code == 404:
            self.state = 'no_authorization'
            return
        res = self.connection.get('/eula/v1/agreement')
        res_json = res.json()

        if res_json['acceptance'] == 'Accepted':
            self.state = 'completed'
            res = self.connection.get('/product-session/v1/sessions')
            return
        self.state = 'agreement_not_accepted'

    def login(self, username, password):
        while True:
            self.update()
            if self.state == 'completed':
                return
            self.do_macro(username, password)
            time.sleep(1)

    def do_macro(self, username, password):
        if self.state == 'no_authorization':
            logging.info('Logging into new riot client')
            res = self.connection.post(
                '/rso-auth/v2/authorizations',
                json={"clientId": "riot-client", "trustLevels": ["always_trusted"]})
            data = {"username": username, "password": password,
                    "persistLogin": False}
            res = self.connection.put(
                '/rso-auth/v1/session/credentials', json=data)
            res_json = res.json()
            if 'message' in res_json:
                if res_json['message'] == 'authorization_error: consent_required: ':
                    raise ConsentRequiredException
            if 'error' in res_json:
                print(res_json)
                if res_json['error'] == 'auth_failure':
                    raise AuthenticationFailureException
                if res_json['error'] == 'rate_limited':
                    logging.info('Rate limited, waiting for 5 minutes')
                    time.sleep(300)
                    return
            return
        if self.state == 'agreement_not_accepted':
            logging.info('Accepting the agreement')
            res = self.connection.put('/eula/v1/agreement/acceptance')
