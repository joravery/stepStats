#!/usr/bin/env python3

"""
Downloads Garmin daily summary data and checks for updated oauth tokens.
"""

__author__ = "Jordan Avery"
__copyright__ = "Copyright Jordan Avery"
__license__ = "GPL"

import datetime

from util.garmin_download import Download


def get_date_and_days(start_date):
    today = datetime.datetime.now().date()
    days = (today - start_date).days + 1
    print(f"date: {start_date}, days: {days}")
    return start_date, days


def get_steps_since_date(start_date, tokens):
    download = Download(tokens=tokens)
    if not download.login():
        raise Exception("Failed to login!")

    date, days = get_date_and_days(start_date)
    if days > 0:
        step_days = download.get_daily_summaries(date, days)
        needs_update, new_tokens = download.check_for_refreshed_tokens()
        return {
            "steps": step_days,
            "needs_update": needs_update,
            "new_tokens": new_tokens
        }
