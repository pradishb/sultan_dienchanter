import configparser
import logging

import lcu_connector_python as lcu
import requests

import re

config = configparser.ConfigParser()
config.read("config/config.cfg")

requests.packages.urllib3.disable_warnings()
logging.getLogger().setLevel(logging.INFO)


class LeagueConnectionException(Exception):
    pass


def connect():
    connection = lcu.connect(config["CLIENT"]["location"])
    if connection == "Ensure the client is running and that you supplied the correct path":
        raise LeagueConnectionException
    return connection


def check_login_session(connection):
    logging.debug("Checking if user is logged in.")
    url = "https://%s/lol-login/v1/session" % connection["url"]
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


def redeem():
    url = "https://%s/lol-loot/v1/player-loot" % connection["url"]
    res = requests.get(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30,)
    res_json = res.json()
    # print(res_json)

    loot_result = list(
        filter(lambda m: re.fullmatch("CHEST_.*", m["lootId"]), res_json))
    if loot_result == []:
        return False

    for loot in loot_result:
        logging.info(
            "Opening chest: %s, Count: %d", loot["lootName"], loot["count"])
        url = "https://%s/lol-loot/v1/recipes/%s_OPEN/craft?repeat=%d" % (
            connection["url"], loot["lootName"], loot["count"])
        data = [loot["lootName"]]
        res = requests.post(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30, json=data)
    return True
    # if loot_result == []:
    #     return False


connection = connect()
# logout(connection)
while not check_login_session(connection):
    login(connection, "Zorlaidricht", "7WRbOphSTbypQTb4")

while True:
    if not redeem():
        break

while check_login_session(connection):
    logout(connection)
# redeem()
# def request(self, path, method, payload=None):
#     if not self.connection:
#         return {}
#     try:
#         url = ("https://" +
#                self.connection["url"] +
#                path)
#         logging.debug(
#             "request,method=%s,url=%s,payload=%s",
#             method, url, payload)
#         res = None
#         if method == "get":
#             res = requests.get(
#                 url,
#                 verify=False,
#                 params=payload,
#                 auth=requests.auth.HTTPBasicAuth(
#                     'riot', self.connection["authorization"]),
#                 timeout=30)
#         if method == "post":
#             res = requests.post(
#                 url,
#                 verify=False,
#                 json=payload,
#                 auth=requests.auth.HTTPBasicAuth(
#                     'riot', self.connection["authorization"]),
#                 timeout=30)
#         if method == "delete":
#             res = requests.delete(
#                 url,
#                 verify=False,
#                 json=payload,
#                 auth=requests.auth.HTTPBasicAuth(
#                     'riot', self.connection["authorization"]),
#                 timeout=30)
#         if method == "patch":
#             res = requests.patch(
#                 url,
#                 verify=False,
#                 json=payload,
#                 auth=requests.auth.HTTPBasicAuth(
#                     'riot', self.connection["authorization"]),
#                 timeout=30)
#         if method == "put":
#             res = requests.put(
#                 url,
#                 verify=False,
#                 json=payload,
#                 auth=requests.auth.HTTPBasicAuth(
#                     'riot', self.connection["authorization"]),
#                 timeout=30)

#         self.log_exception(url, res)
#         return res
#     except requests.exceptions.Timeout:
#         logging.error("Request timeout.")
#         sys.exit()
#     except json.decoder.JSONDecodeError:
#         self.log_exception(url, res)
#         return res
#     except requests.exceptions.ConnectionError:
#         self.log_exception(url, res)
#         return res
#     except TypeError:
#         logging.error('Exception in APIClient class')
#         return {}

# def log_exception(self, url, res):
#     try:
#         logging.debug("response,url=%s,status=%s", url, res.status_code)
#     except AttributeError:
#         logging.debug("response,url=%s,status=%s", url, "None")
