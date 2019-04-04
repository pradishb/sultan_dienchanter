import logging
import time

import requests


def check_login_session(connection):
    logging.debug("Checking if user is logged in.")
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
            return False
        return False
    except requests.RequestException:
        return False


def login(connection, username, password):
    logging.info("Logging in. Username: %s Password: %s", username, password)
    data = {
        "password": password,
        "username": username,
    }
    url = "https://%s/lol-login/v1/session" % connection["url"]
    requests.post(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30,
        json=data)


def logout(connection):
    logging.info("Logging out")
    url = "https://%s/lol-login/v1/session" % connection["url"]
    requests.delete(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30,)


def login_loop(connection, account):
    while not check_login_session(connection):
        login(connection, account[0], account[1])
        time.sleep(1)
