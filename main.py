import argparse
import configparser
import csv
import logging
import re
import sys
import os
import time

import lcu_connector_python as lcu
import requests
import subprocess


config = configparser.ConfigParser()
config.read("config/config.cfg")

requests.packages.urllib3.disable_warnings()
logging.getLogger().setLevel(logging.INFO)


class LeagueConnectionException(Exception):
    pass


class LootRetrieveException(Exception):
    pass


def connect():
    connection = lcu.connect(config["CLIENT"]["location"])
    if connection == "Ensure the client is running and that you supplied the correct path":
        raise LeagueConnectionException
    return connection


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


def get_loot(connection):
    logging.info("Retrieving loot")
    url = "https://%s/lol-loot/v1/player-loot" % connection["url"]
    res = requests.get(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30,)
    res_json = res.json()
    if res_json == []:
        logging.error("Can't retrieve loot")
        raise LootRetrieveException
    return res_json


def open_chests(connection):
    logging.info("Checking chests")
    try:
        res_json = get_loot(connection)
    except LootRetrieveException:
        return False

    loot_result = list(
        filter(lambda m: re.fullmatch("CHEST_.*", m["lootId"]), res_json))
    if loot_result == []:
        return True

    for loot in loot_result:
        logging.info(
            "Opening chest: %s, Count: %d", loot["lootName"], loot["count"])
        url = "https://%s/lol-loot/v1/recipes/%s_OPEN/craft?repeat=%d" % (
            connection["url"], loot["lootName"], loot["count"])
        data = [loot["lootName"]]
        res = requests.post(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30, json=data)
    return False


def disenchant(connection):
    try:
        res_json = get_loot(connection)
    except LootRetrieveException:
        return False

    loot_result = list(
        filter(lambda m: m["displayCategories"] == "CHAMPION", res_json))
    if loot_result == []:
        return True

    for loot in loot_result:
        logging.info(
            "Dienchanting: %s, Count: %d", loot["itemDesc"], loot["count"])
        url = "https://%s/lol-loot/v1/recipes/%s_disenchant/craft?repeat=%d" % (
            connection["url"], loot["type"], loot["count"])
        data = [loot["lootName"]]
        requests.post(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30, json=data)
    return False


def read_accounts():
    accounts = []
    with open("accounts.txt") as file:
        reader = csv.reader(file, delimiter=":")
        for row in reader:
            accounts.append(row)
    return accounts


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

    for account in accounts:
        os.system('taskkill /f /im LeagueClient.exe')
        logging.info(
            "Current Account: %s, Password: %s", account[0], account[1])
        process = open_league_client()
        time.sleep(5)
        connection = connect()
        while not check_login_session(connection):
            login(connection, account[0], account[1])
            time.sleep(1)

        while True:
            if open_chests(connection):
                break
            time.sleep(1)

        while True:
            if disenchant(connection):
                break
            time.sleep(1)
