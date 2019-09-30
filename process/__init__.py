'''
Module that handles tasks related to processes
'''
import os
import subprocess
import time

import psutil

from settings import GAME_PROCESS_LOCAITON, GAME_PROCESS


def is_running(process_name):
    '''
    Check if there is any running process that contains
    the given name process_name.
    '''
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess,
                psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def open_game():
    '''
    Opens a instance of game
    '''
    process = subprocess.Popen([GAME_PROCESS_LOCAITON])
    return process


def close_game():
    '''
    Closes the game
    '''
    while True:
        for proc in psutil.process_iter():
            if proc.name() == GAME_PROCESS:
                proc.kill()
        if not is_running(GAME_PROCESS):
            return
        time.sleep(1)


def restart_game():
    '''
    Restarts the game
    '''
    close_game()
    open_game()
