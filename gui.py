import configparser
import logging
import subprocess as sub
import sys
import threading
import time
import tkinter as tk

logging.getLogger().setLevel(logging.INFO)


class LogWriter(object):
    def __init__(self, app):
        self.app = app

    def write(self, data):
        self.app.write_console(data)


class Application:
    def __init__(self, master):
        logger = LogWriter(self)
        sys.stderr = logger

        callbacks = {
            'start': self.start,
            'import_csv': self.start,
            'export_csv': self.start,
        }

        import pygubu
        self.master = master
        self.master.title("Sultan Disenchanter")
        self.builder = builder = pygubu.Builder()
        self.builder.add_from_file('main_frame.ui')
        self.mainwindow = builder.get_object('main_frame', master)
        self.builder.connect_callbacks(callbacks)

    def set_entry(self, name, value):
        self.builder.get_object(name).delete(0, tk.END)
        self.builder.get_object(name).insert(0, str(value))

    def set_checkbox(self, name, value):
        if value:
            self.builder.get_object(name).select()
        else:
            self.builder.get_object(name).deselect()

    def write_console(self, text):
        self.builder.get_object("console").insert(tk.END, text)
        self.builder.get_object("console").see("end")

    def start(self):
        logging.info("asdfds")
        print("hello")


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
