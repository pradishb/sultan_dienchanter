import logging
import re

import requests


class LootRetrieveException(Exception):
    pass


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
    logging.info("Opening chests")
    try:
        res_json = get_loot(connection)
    except LootRetrieveException:
        return "error"

    loot_result = list(
        filter(lambda m: re.fullmatch("CHEST_.*", m["lootId"]), res_json))
    if loot_result == []:
        return "done"

    for loot in loot_result:
        logging.info(
            "Opening chest: %s, Count: %d", loot["lootName"], loot["count"])
        url = "https://%s/lol-loot/v1/recipes/%s_OPEN/craft?repeat=%d" % (
            connection["url"], loot["lootName"], loot["count"])
        data = [loot["lootName"]]
        requests.post(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30, json=data)
    return "progress"


def disenchant(connection):
    logging.info("Disenchanting champion shards")
    try:
        res_json = get_loot(connection)
    except LootRetrieveException:
        return "error"

    loot_result = list(
        filter(lambda m: m["displayCategories"] == "CHAMPION", res_json))
    if loot_result == []:
        return "done"

    for loot in loot_result:
        logging.info(
            "Dienchanting: %s, Count: %d", loot["itemDesc"], loot["count"])
        url = "https://%s/lol-loot/v1/recipes/%s_disenchant/craft?repeat=%d" % (
            connection["url"], loot["type"], loot["count"])
        data = [loot["lootName"]]
        requests.post(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30, json=data)
    return "progress"


def process_redeem(connection, array):
    for loot in array:
        logging.info(
            "Redeeming: %s, Count: %d", loot["itemDesc"], loot["count"])
        url = "https://%s/lol-loot/v1/player-loot/%s/redeem" % (
            connection["url"], loot["lootName"])
        requests.post(
            url, verify=False, auth=('riot', connection["authorization"]), timeout=30)


def redeem_free(connection):
    logging.info("Redeeming free shards")
    try:
        res_json = get_loot(connection)
    except LootRetrieveException:
        return "error"

    loot_result = list(
        filter(lambda m: (
            m["upgradeEssenceValue"] == 0 and
            m["type"] == "CHAMPION" and
            m["redeemableStatus"] == "REDEEMABLE"
        ), res_json))
    if loot_result == []:
        return "done"

    process_redeem(connection, loot_result)
    return "progress"


def redeem(connection, value):
    logging.info("Redeeming %d BE shards", value)
    try:
        res_json = get_loot(connection)
    except LootRetrieveException:
        return "error"

    loot_result = list(
        filter(lambda m: (
            m["value"] == value and
            m["type"] == "CHAMPION_RENTAL" and
            m["redeemableStatus"] == "REDEEMABLE_RENTAL"
        ), res_json))

    if loot_result == []:
        return "done"

    process_redeem(connection, loot_result)
    return "progress"
