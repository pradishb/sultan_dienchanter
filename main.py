import argparse
import configparser
import csv
import logging
import re
import sys
import os
import time

import store
import account
import loot
import lcu_connector_python as lcu
import requests
import subprocess


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


def open_league_client():
    path = os.path.join(config["CLIENT"]["location"], "LeagueClient.exe")
    process = subprocess.Popen(
        [path, "--headless"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


if __name__ == "__main__":
    try:
        accounts = read_accounts()
    except FileNotFoundError:
        logging.error("Accounts file not found")
        sys.exit()

    for acc in accounts:
        os.system('taskkill /f /im LeagueClient.exe')
        logging.info(
            "Current Account: %s, Password: %s", acc[0], acc[1])
        process = open_league_client()
        time.sleep(5)
        connection = connect()
        while not account.check_login_session(connection):
            account.login(connection, acc[0], acc[1])
            time.sleep(1)

        while True:
            if loot.open_chests(connection) == "done":
                break
            time.sleep(1)

        while True:
            if loot.redeem_free(connection) == "done":
                break
            time.sleep(1)

        while True:
            if loot.redeem(connection, 450) == "done":
                break
            time.sleep(1)

        while True:
            if loot.redeem(connection, 1350) == "done":
                break
            time.sleep(1)

        while True:
            if loot.disenchant(connection) == "done":
                break
            time.sleep(1)

        store.buy_champ_by_be(connection, 450)
        store.buy_champ_by_be(connection, 1350)
    os.system('taskkill /f /im LeagueClient.exe')
