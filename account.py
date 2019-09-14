import logging
import time

import requests


class AccountBannedException(Exception):
    pass


class InvalidCredentialsException(Exception):
    pass


def check_login_session(connection):
    url = "https://%s/lol-login/v1/session" % connection["url"]
    try:
        res = requests.get(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
        res_json = res.json()
        if res.status_code == 404:
            return False

        if res_json["state"] == "SUCCEEDED":
            return True
        if res_json["state"] == "ERROR":
            if res_json["error"]["messageId"] == "ACCOUNT_BANNED":
                raise AccountBannedException
            if res_json["error"]["messageId"] == "INVALID_CREDENTIALS":
                raise InvalidCredentialsException
            return False
        return False
    except requests.RequestException:
        return False


def login(connection, username, password):
    try:
        data = {
            "password": password,
            "username": username,
        }
        url = "https://%s/lol-login/v1/session" % connection["url"]
        requests.post(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30,
            json=data)
    except requests.RequestException:
        return


def logout(connection):
    try:
        logging.info("Logging out")
        url = "https://%s/lol-login/v1/session" % connection["url"]
        requests.delete(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30,)
    except requests.RequestException:
        return


def login_loop(connection, account):
    logging.info(
        "Logging in. Username: %s Password: %s", account[0], account[1])
    while not check_login_session(connection):
        login(connection, account[0], account[1])
        time.sleep(1)
