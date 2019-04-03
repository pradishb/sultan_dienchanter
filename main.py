import configparser

import logging
import lcu_connector_python as lcu

config = configparser.ConfigParser()
config.read("config/config.cfg")
print(config["CLIENT"]["locaiton"])

# connection = None


# def connect(self):
#     try:
#         self.connection = lcu.connect(config.Config.value["location"])
#         logging.debug(self.connection)
#         if 'authorization' in self.connection:
#             return True
#     except KeyError:
#         logging.error(
#             "Error retriving client key. Ensure the client is open.")
#     return False

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
