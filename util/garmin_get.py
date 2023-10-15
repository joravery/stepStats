#!/usr/bin/env python3

"""
A script that downloads Garmin daily summary data.
"""

__author__ = "Jordan Avery"
__copyright__ = "Copyright Jordan Avery"
__license__ = "GPL"

import sys
import datetime
import json

from util.garmin_download import Download

def get_date_and_days(start_date):
    today = datetime.datetime.now().date()
    days = (today - start_date).days + 1
    print(f"date: {start_date}, days: {days}")
    return (start_date, days)


def download_data(overwite, username, password, start_date):
    """Download daily summaries Garmin Connect and save the data in files"""

    download = Download()
    if not download.login(username, password):
        print("Failed to login!")
        sys.exit()

    date, days = get_date_and_days(start_date)
    if days > 0:
        print("Date range to update: %s (%d) to %s", date, days, "/tmp")
        files_downloaded = download.get_daily_summaries("/tmp", date, days, overwite)
        return files_downloaded

def load_steps_from_file(file):
    for k, v in file.items():
        path = v
        date = k
        with open(path, "r") as file:
            f = json.load(file)
            return {'date': date, 'steps': f['totalSteps']}

def garmin_get_steps_since_last_date(start_date, username, password):
    print("Fetching data from Garmin Connect...")
    overwrite = True
    files = download_data(overwrite, username, password, start_date)
    steps = []
    for file in files:
        print(f"File: {file}")
        steps.append(load_steps_from_file(file))
    return steps
