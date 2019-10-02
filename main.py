import configparser
import logging
import subprocess as sub
import sys
import threading
import time
import tkinter as tk

import urllib3

import file_handler
from process import kill_process
from account import AccountBannedException, InvalidCredentialsException
from client.league import do_macro
from client.riot import RiotClient
from client.exceptions import AuthenticationFailureException, ConsentRequiredException
from settings import LEAGUE_CLIENT_PROCESS, RIOT_CLIENT_PROCESS

logging.getLogger().setLevel(logging.INFO)
urllib3.disable_warnings()


class LogWriter(object):
    def __init__(self, app):
        sys.stderr = self
        self.app = app

    def write(self, data):
        self.app.write_console(data)


class Application:
    def __init__(self, master):
        LogWriter(self)

        self.accounts = []

        import pygubu
        self.master = master
        self.master.title("Sultan Disenchanter")
        self.builder = builder = pygubu.Builder()
        self.builder.add_from_file('main_frame.ui')
        self.mainwindow = builder.get_object('main_frame', master)
        self.builder.connect_callbacks(self)
        self.init_checkboxes()
        self.riot_client = RiotClient()

    def init_checkboxes(self):
        self.init_checkbox("open_chests", True)
        self.init_checkbox("redeem_free", True)
        self.init_checkbox("redeem_450", True)
        self.init_checkbox("redeem_1350", True)
        self.init_checkbox("redeem_3150", True)
        self.init_checkbox("redeem_4800", True)
        self.init_checkbox("redeem_6300", True)
        self.init_checkbox("disenchant", True)
        self.init_checkbox("buy_450", True)
        self.init_checkbox("buy_1350", True)
        self.init_checkbox("buy_3150", True)
        self.init_checkbox("buy_4800", True)
        self.init_checkbox("buy_6300", True)
        self.init_checkbox("read_be", True)
        self.init_checkbox("read_owned", True)
        self.init_checkbox("change_icon", True)

    def start(self):
        if self.accounts == []:
            logging.error("No accounts imported")
            return
        self.clear_treeview("accounts")
        thread = threading.Thread(target=self.start_macro)
        thread.daemon = True
        thread.start()

    def start_macro(self):
        options = [
            self.builder.get_object('open_chests').instate(['selected']),
            self.builder.get_object('redeem_free').instate(['selected']),
            self.builder.get_object('redeem_450').instate(['selected']),
            self.builder.get_object('redeem_1350').instate(['selected']),
            self.builder.get_object('redeem_3150').instate(['selected']),
            self.builder.get_object('redeem_4800').instate(['selected']),
            self.builder.get_object('redeem_6300').instate(['selected']),
            self.builder.get_object('disenchant').instate(['selected']),
            self.builder.get_object('buy_450').instate(['selected']),
            self.builder.get_object('buy_1350').instate(['selected']),
            self.builder.get_object('buy_3150').instate(['selected']),
            self.builder.get_object('buy_4800').instate(['selected']),
            self.builder.get_object('buy_6300').instate(['selected']),
            self.builder.get_object('read_be').instate(['selected']),
            self.builder.get_object('read_owned').instate(['selected']),
            self.builder.get_object('change_icon').instate(['selected']),
        ]
        self.builder.get_object("start")['state'] = 'disabled'

        kill_process(LEAGUE_CLIENT_PROCESS)
        kill_process(RIOT_CLIENT_PROCESS)
        for idx, account in enumerate(self.accounts):
            try:
                res = do_macro(self.riot_client, account, options)
            except AccountBannedException:
                res = [0, 0]
                logging.info("Account %s is banned", account[0])
            except (InvalidCredentialsException, AuthenticationFailureException):
                res = [0, 0]
                logging.info("Account %s has invalid credentials", account[0])
            except ConsentRequiredException:
                res = [0, 0]
                logging.info("Account %s needs consent", account[0])
            progress = (idx + 1) * 100 // len(self.accounts)
            account = account + res
            self.accounts[idx] = account
            self.set_row("accounts", account)
            self.builder.get_object("progress")["value"] = progress
        self.builder.get_object("start")['state'] = 'normal'

    def import_csv(self):
        self.accounts = file_handler.import_csv()
        self.set_treeview("accounts", self.accounts)

    def export_csv(self):
        if file_handler.export_csv(self.accounts):
            logging.info("Successfully exported")

    def set_entry(self, name, value):
        self.builder.get_object(name).delete(0, tk.END)
        self.builder.get_object(name).insert(0, str(value))

    def set_treeview(self, name, values):
        for value in values:
            self.set_row(name, value)

    def clear_treeview(self, name):
        tree = self.builder.get_object(name)
        tree.delete(*tree.get_children())

    def set_row(self, name, value):
        self.builder.get_object(name).insert(
            '', 'end', values=value)

    def init_checkbox(self, name, value):
        self.builder.get_object(name).state(['!alternate'])
        if value:
            self.builder.get_object(name).state(['selected'])
        else:
            self.builder.get_object(name).state(['!selected'])

    def write_console(self, text):
        self.builder.get_object("console").insert(tk.END, text)
        self.builder.get_object("console").see("end")


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
