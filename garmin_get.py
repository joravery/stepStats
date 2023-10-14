#!/usr/bin/env python3

"""
A script that downloads Garmin daily summary data.
"""

__author__ = "Jordan Avery"
__copyright__ = "Copyright Jordan Avery"
__license__ = "GPL"

import logging
import sys
import datetime

from util.garmin_download import Download


logging.basicConfig(filename='garmindb.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
root_logger = logging.getLogger()


def __get_date_and_days():
    date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    days = 2
    print(f"date: {date}, days: {days}")
    return (date, days)


def download_data(overwite, latest):
    """Download selected activity types from Garmin Connect and save the data in files. Overwrite previously downloaded data if indicated."""
    logger.info("___Downloading %s Data___", 'Latest' if latest else 'All')

    download = Download()
    if not download.login("jordan.avery1@gmail.com", "REDACTED"):
        logger.error("Failed to login!")
        sys.exit()


    date, days = __get_date_and_days()
    if days > 0:
        root_logger.info("Date range to update: %s (%d) to %s", date, days, "/tmp")
        download.get_daily_summaries("/tmp", date, days, overwite)
        root_logger.info("Saved monitoring files for %s (%d) to %s for processing", date, days, "/tmp")
        

def main(argv):
    root_logger.setLevel(logging.DEBUG)

    print("Fetching data from Garmin Connect...")
    download_data(True, True)

if __name__ == "__main__":
    main(sys.argv[1:])
