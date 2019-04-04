import configparser
import logging
import subprocess as sub
import sys
import threading
import time
import tkinter as tk

import client
import file_handler

logging.getLogger().setLevel(logging.INFO)


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
        # self.master.withdraw()

    def init_checkboxes(self):
        self.set_checkbox("open_chests", True)
        self.set_checkbox("redeem_free", True)
        self.set_checkbox("redeem_450", True)
        self.set_checkbox("redeem_1350", True)
        self.set_checkbox("disenchant", True)
        self.set_checkbox("buy_450", True)
        self.set_checkbox("buy_1350", True)
        self.set_checkbox("read_be", True)
        self.set_checkbox("read_owned", True)

    def start(self):
        if self.accounts == []:
            logging.error("No accounts imported")
            return
        self.clear_treeview("accounts")
        threading.Thread(target=self.start_macro).start()

    def start_macro(self):
        for idx, account in enumerate(self.accounts):
            res = client.do_macro(account, [
                False, False, False, False, False, False, False, True, True])
            account = account + res
            self.accounts[idx] = account
            self.set_row("accounts", account)
            print(self.accounts)

    def import_csv(self):
        self.accounts = file_handler.import_csv()
        self.set_treeview("accounts", self.accounts)

    def export_csv(self):
        print(file_handler.import_csv())

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

    def set_checkbox(self, name, value):
        if value:
            self.builder.get_object(name).select()
        else:
            self.builder.get_object(name).deselect()

    def write_console(self, text):
        self.builder.get_object("console").insert(tk.END, text)
        self.builder.get_object("console").see("end")


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
