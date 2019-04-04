import logging
import time

import requests


def check_owned(connection):
    logging.info("Checking number of champions owned")
    url = "https://%s/lol-champions/v1/owned-champions-minimal" % connection["url"]
    res = requests.get(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
    if res.status_code == 404:
        return "not_found"
    res_json = res.json()
    print(res_json)
    filtered = list(
        filter(lambda m: m["ownership"]["owned"], res_json))

    logging.info("%d champs owned bitch", len(filtered))
    return "done"


def check_owned_loop(connection):
    while True:
        if check_owned(connection) == "done":
            break
        time.sleep(1)


def get_be(connection):
    logging.info("Checking blue essence")
    url = "https://%s/lol-store/v1/wallet" % connection["url"]
    res = requests.get(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
    res_json = res.json()
    return res_json['ip']
