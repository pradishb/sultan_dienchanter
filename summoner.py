import logging
import time

import requests


def change_icon(connection, icon_id):
    url = "https://%s/lol-summoner/v1/current-summoner/icon" % connection["url"]
    json = {
        "profileIconId": icon_id
    }
    try:
        logging.info("Changing summoner icon")
        requests.put(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30, json=json)
    except requests.RequestException:
        return False


def get_icon(connection):
    try:
        url = "https://%s/lol-summoner/v1/current-summoner" % connection["url"]
        res = requests.get(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
        res_json = res.json()
        return res_json["profileIconId"]
    except requests.RequestException:
        return -1


def change_icon_loop(connection, icon_id):
    while get_icon(connection) != icon_id:
        change_icon(connection, icon_id)
        time.sleep(1)
