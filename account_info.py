import logging
import time

import requests


class ClientResponseError(Exception):
    pass


def check_owned(connection):
    url = "https://%s/lol-champions/v1/owned-champions-minimal" % connection["url"]
    res = requests.get(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
    if res.status_code == 404:
        raise ClientResponseError
    res_json = res.json()
    if res_json == []:
        raise ClientResponseError
    filtered = list(
        filter(lambda m: m["ownership"]["owned"], res_json))

    return len(filtered)


def check_owned_loop(connection):
    logging.info("Checking number of champions owned")
    while True:
        try:
            return check_owned(connection)
        except ClientResponseError:
            pass
        time.sleep(1)


def get_be(connection):
    logging.info("Checking blue essence")
    url = "https://%s/lol-store/v1/wallet" % connection["url"]
    res = requests.get(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
    res_json = res.json()
    return res_json['ip']
