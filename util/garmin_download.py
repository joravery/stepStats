"""Class for downloading step data from Garmin Connect."""
"""Heavily modified from https://github.com/tcgoetz/GarminDB/"""
"""Original author: Tom Goetz"""

import datetime
import time
import random
from garth import Client as GarthClient
from garth.exc import GarthHTTPError
from tqdm import tqdm

import fitfile.conversions as conversions

class Download():
    """Class for downloading health data from Garmin Connect."""

    garmin_connect_usersummary_url = "/usersummary-service/usersummary"
    garmin_connect_daily_summary_url = garmin_connect_usersummary_url + "/daily"
    garmin_base_domain = "garmin.com"

    def __init__(self):
        """Create a new Download class instance."""
        self.garth = GarthClient()
        self.garth.configure(domain=self.garmin_base_domain)

    def login(self, username, password):
        """Login to Garmin Connect."""
        if not username or not password:
            print("Missing config: need username and password")
            return

        print(f"login user: {username}, pass: {password[:4] + len(password[4:]) * '*'}")
        self.garth.login(username, password)

        self.social_profile = self.garth.profile
        self.user_prefs = self.garth.profile
        self.display_name = self.social_profile['displayName']
        self.full_name = self.social_profile['fullName']
        print(f"succesful login: {self.full_name} ({self.display_name})")
        return True

    def get_daily_summary(self, date):
        print(f"get_summary_day: {date}" )
        date_str = date.strftime('%Y-%m-%d')
        params = {
            'calendarDate': date_str,
            '_': str(conversions.dt_to_epoch_ms(conversions.date_to_dt(date)))
        }
        url = f'{self.garmin_connect_daily_summary_url}/{self.display_name}'
        
        try:
            connect_response = self.garth.connectapi(url, params=params)
            return {'date' :date_str, 'steps' : connect_response['totalSteps']}
        except GarthHTTPError as e:
            print(f"Exception getting daily summary: {e}")

    def get_daily_summaries(self, date, days):
        """Download the daily summary data from Garmin Connect and save to a JSON file."""
        print(f"Getting daily summaries: {date} ({days})")
        step_days = []
        for day in tqdm(range(0, days), unit='days'):
            download_date = date + datetime.timedelta(days=day)
            file_path = self.get_daily_summary( download_date)
            step_days.append(file_path)
            # Sleep for between 1 and 2 seconds to avoid getting blocked by Garmin
            # for too many requests.
            if days > 3:
                time.sleep(1 + random.random())
        return step_days
