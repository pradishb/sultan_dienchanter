import logging
import os
import subprocess
import time

import lcu_connector_python as lcu
import urllib3
import requests

import account
import account_info
import loot
import store
import summoner
from process import is_running
from settings import (LEAGUE_CLIENT_PATH, LEAGUE_CLIENT_PROCESS,
                      RIOT_CLIENT_PROCESS, RIOT_CLIENT_SERVICES_PATH)

HANDLERS = [
    (loot.open_chests_loop, []),
    (loot.redeem_free_loop, []),
    (loot.redeem_loop, [450]),
    (loot.redeem_loop, [1350]),
    (loot.redeem_loop, [3150]),
    (loot.redeem_loop, [4850]),
    (loot.redeem_loop, [6300]),
    (loot.disenchant_loop, []),
    (store.buy_champ_by_be, [450]),
    (store.buy_champ_by_be, [1350]),
    (store.buy_champ_by_be, [3150]),
    (store.buy_champ_by_be, [4800]),
    (store.buy_champ_by_be, [6300]),
    (account_info.get_be, []),
    (account_info.check_owned_loop, []),
    (summoner.change_icon_loop, [23]),
]


def connect():
    while True:
        connection = lcu.connect(LEAGUE_CLIENT_PATH)
        if connection != "Ensure the client is running and that you supplied the correct path":
            if check_lcu_online(connection):
                return connection
        time.sleep(1)


def open_riot_client():
    if is_running(LEAGUE_CLIENT_PROCESS) or is_running(RIOT_CLIENT_PROCESS):
        return
    logging.info('Starting riot client')
    process = subprocess.Popen([
        RIOT_CLIENT_SERVICES_PATH,
        "--headless",
        "--launch-product=league_of_legends",
        "--launch-patchline=live"])
    return process


def open_league_client():
    if is_running(LEAGUE_CLIENT_PROCESS):
        return
    logging.info('Starting league client')
    process = subprocess.Popen([
        LEAGUE_CLIENT_PATH,
        "--headless"])
    return process


def check_lcu_online(connection):
    try:
        url = "https://%s/lol-service-status/v1/lcu-status" % connection["url"]
        res = requests.get(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
        res_json = res.json()
        if 'status' in res_json:
            if res_json["status"] == 'online':
                return True
    except requests.exceptions.RequestException:
        return False
    return False


def do_macro(riot_client, acc, options):
    open_riot_client()
    logging.info("Current Account: %s, Password: %s", acc[0], acc[1])
    riot_client.login(acc[0], acc[1])
    open_league_client()
    connection = connect()
    result = {
        13: None,
        14: None,
    }

    for key in range(len(options)):
        if not options[key]:
            continue
        result[key] = HANDLERS[key][0](connection, *HANDLERS[key][1])
    riot_client.logout(connection)

    logging.info("Done")

    return [result[13], result[14]]
