import logging

import requests


def catalog(connection, type):
    logging.info("Getting store item catalog for type %s", type)

    url = "https://%s/lol-store/v1/catalog?inventoryType=[\"%s\"]" % (
        connection["url"], type)
    res = requests.get(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30)
    return res.json()


def buy_champ_by_be(connection, be):
    logging.info("Getting champions at costs %d BE", be)
    res_json = catalog(connection, "CHAMPION")
    filtered = list(
        filter(lambda m: m["prices"][0]["cost"] == be, res_json))
    for champ in filtered:
        name = champ["localizations"]["en_GB"]["name"]
        result = buy(connection, name,
                     champ["itemId"], champ["prices"][0]["cost"])
        if result == "validation.item.owned":
            logging.info("Champion already owned")
            continue
        if result == "validation.item.not.enough.currency":
            logging.info("Not enough BE to buy champion")
            break


def buy(connection, name, item_id, val):
    data = {
        "items": [
            {
                "itemKey": {
                    "inventoryType": "CHAMPION",
                    "itemId": item_id
                },
                "purchaseCurrencyInfo": {
                    "currencyType": "IP",
                    "price": val,
                    "purchasable": True,
                },
                "quantity": 1
            }
        ]
    }
    logging.info(
        "Buying %s", name)
    url = "https://%s/lol-purchase-widget/v1/purchaseItems" % (
        connection["url"])
    res = requests.post(
        url, verify=False, auth=('riot', connection["authorization"]), timeout=30, json=data)
    res_json = res.json()
    if res.status_code == 200:
        return "success"
    return res_json["errorDetails"].popitem()[0]
