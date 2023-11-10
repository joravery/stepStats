import datetime
import random
import time

import fitfile.conversions as conversions
from garth import Client as GarthClient
from garth.exc import GarthHTTPError
from tqdm import tqdm

"""Class for downloading step data from Garmin Connect."""
"""Heavily modified from https://github.com/tcgoetz/GarminDB/"""
"""Original author: Tom Goetz"""


class Download:
    """Class for downloading health data from Garmin Connect."""

    garmin_connect_user_summary_url = "/usersummary-service/usersummary"
    garmin_connect_daily_summary_url = garmin_connect_user_summary_url + "/daily"
    garmin_base_domain = "garmin.com"

    def __init__(self, tokens=None):
        """Create a new Download class instance."""
        self.display_name = ""
        self.full_name = ""
        self.garth = GarthClient()
        self.original_tokens = tokens
        self.garth.loads(tokens)

    def login(self) -> bool:
        """Login to Garmin Connect."""
        try:
            self.display_name = self.garth.profile['displayName']
            self.full_name = self.garth.profile['fullName']
            print(f"successful login. Name: {self.full_name}, User GUID: ({self.display_name})")
            return True
        except GarthHTTPError as e:
            print(f"failed to login, likely need to refresh oath1 token {e}")
            return False

    def get_daily_summary(self, date) -> dict:
        print(f"get_summary_day: {date}")
        date_str = date.strftime('%Y-%m-%d')
        params = {'calendarDate': date_str, '_': str(conversions.dt_to_epoch_ms(conversions.date_to_dt(date)))}
        url = f'{self.garmin_connect_daily_summary_url}/{self.display_name}'

        try:
            connect_response = self.garth.connectapi(url, params=params)
            return {'date': date_str, 'steps': connect_response['totalSteps']}
        except GarthHTTPError as e:
            print(f"Exception getting daily summary: {e}")

    def get_daily_summaries(self, date, days) -> list:
        """Download the daily summary data from Garmin Connect and save to a JSON file."""
        print(f"Getting daily summaries: {date} ({days})")
        step_days = []
        for day in tqdm(range(0, days), unit='days'):
            download_date = date + datetime.timedelta(days=day)
            file_path = self.get_daily_summary(download_date)
            step_days.append(file_path)
            # Sleep for between 1 and 2 seconds to avoid getting blocked by Garmin
            if days > 3:
                time.sleep(1 + random.random())
        return step_days

    def check_for_refreshed_tokens(self) -> (bool, str):
        original_tokens = self.original_tokens
        current_tokens = self.garth.dumps()
        if original_tokens != current_tokens:
            print("Tokens have been updated")
            return True, current_tokens
        else:
            print("Tokens have not been updated")
            return False, None
