import argparse
import configparser
import csv
import logging
import os
import re
import subprocess
import sys
import time

import lcu_connector_python as lcu
import requests

import account
import account_info
import loot
import store
import summoner

config = configparser.ConfigParser()
config.read("config/config.cfg")

requests.packages.urllib3.disable_warnings()

HANDLERS = [
    (loot.open_chests_loop, []),
    (loot.redeem_free_loop, []),
    (loot.redeem_loop, [450]),
    (loot.redeem_loop, [1350]),
    (loot.disenchant_loop, []),
    (store.buy_champ_by_be, [450]),
    (store.buy_champ_by_be, [1350]),
    (account_info.get_be, []),
    (account_info.check_owned_loop, []),
    (summoner.change_icon_loop, [23]),
]


class LeagueConnectionException(Exception):
    pass


def connect():
    connection = lcu.connect(config["CLIENT"]["location"])
    if connection == "Ensure the client is running and that you supplied the correct path":
        raise LeagueConnectionException
    return connection


def open_league_client():
    path = os.path.join(config["CLIENT"]["location"], "LeagueClient.exe")
    process = subprocess.Popen([path, "--headless"])
    return process


def do_macro(acc, options):
    os.system('taskkill /f /im LeagueClient.exe')
    logging.info("Current Account: %s, Password: %s", acc[0], acc[1])
    open_league_client()
    time.sleep(5)
    connection = connect()
    account.login_loop(connection, acc)

    result = {
        7: None,
        8: None,
    }

    for key in range(len(options)):
        if not options[key]:
            continue
        result[key] = HANDLERS[key][0](connection, *HANDLERS[key][1])

    os.system('taskkill /f /im LeagueClient.exe')
    logging.info("Done")

    return [result[7], result[8]]
