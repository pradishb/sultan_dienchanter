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


def export_csv(data):
    file = filedialog.asksaveasfilename()
    try:
        with open(file, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=":")
            for row in data:
                writer.writerow(row)
    except FileNotFoundError:
        return False
    return True
