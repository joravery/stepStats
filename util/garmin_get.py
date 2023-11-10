#!/usr/bin/env python3

"""
Downloads Garmin daily summary data and checks for updated oauth tokens.
"""

__author__ = "Jordan Avery"
__copyright__ = "Copyright Jordan Avery"
__license__ = "GPL"

from util.garmin_download import Download


def get_steps_since_date(end_date, num_days, tokens):
    download = Download(tokens=tokens)
    if not download.login():
        raise Exception("Failed to login!")

    step_days = download.get_daily_summaries(end_date, num_days)
    needs_update, new_tokens = download.check_for_refreshed_tokens()
    return {"steps": step_days, "needs_update": needs_update, "new_tokens": new_tokens}
