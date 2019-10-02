import logging
import time

import requests

from .exceptions import AccountBannedException, InvalidCredentialsException


def check_login_session(connection):
    while True:
        url = "https://%s/lol-login/v1/session" % connection["url"]
        try:
            res = requests.get(
                url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
            res_json = res.json()
            if res_json["state"] == "SUCCEEDED":
                return
            if res_json["state"] == "ERROR":
                if res_json["error"]["messageId"] == "ACCOUNT_BANNED":
                    raise AccountBannedException
                if res_json["error"]["messageId"] == "INVALID_CREDENTIALS":
                    raise InvalidCredentialsException
        except requests.RequestException:
            pass
        finally:
            time.sleep(0.1)


def logout(connection):
    try:
        logging.info("Logging out")
        url = "https://%s/lol-login/v1/session" % connection["url"]
        requests.delete(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30,)
    except requests.RequestException:
        return


def login(account):
    logging.info(
        "Logging in. Username: %s Password: %s", account[0], account[1])
