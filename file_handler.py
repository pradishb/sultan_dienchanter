import csv

from tkinter import filedialog


def import_csv():
    file = filedialog.askopenfile("r")

    if file is None:
        return []
    accounts = []
    reader = csv.reader(file, delimiter=":")
    for row in reader:
        accounts.append(row)
    return accounts


def export_csv():
    file = filedialog.askopenfile("w")
    print(file)
