"""Class for downloading step data from Garmin Connect."""
"""Heavily modified from https://github.com/tcgoetz/GarminDB/"""
"""Original author: Tom Goetz"""

import os
import datetime
import time
import json
import random
from garth import Client as GarthClient
from garth.exc import GarthHTTPError
from tqdm import tqdm

import fitfile.conversions as conversions

class Download():
    """Class for downloading health data from Garmin Connect."""

    garmin_connect_user_profile_url = "/userprofile-service/userprofile"
    garmin_connect_usersummary_url = "/usersummary-service/usersummary"
    garmin_connect_daily_summary_url = garmin_connect_usersummary_url + "/daily"
    garmin_base_domain = "garmin.com"

    def __init__(self):
        """Create a new Download class instance."""
        self.garth = GarthClient()
        self.garth.configure(domain=self.garmin_base_domain)

    def login(self, username, password, base_dir="/tmp"):
        """Login to Garmin Connect."""
        profile_dir = base_dir
        if not username or not password or not profile_dir:
            print("Missing config: need username, password, and base_dir.")
            return

        print("login: %s %s", username, password[:4] + len(password[4:]) * '*')
        self.garth.login(username, password)

        self.social_profile = self.garth.profile
        self.user_prefs = self.garth.profile

        if profile_dir:
            self.save_json_to_file(f'{profile_dir}/social-profile', self.social_profile)
            self.save_json_to_file(f'{profile_dir}/user-settings', self.garth.connectapi(f'{self.garmin_connect_user_profile_url}/user-settings'))
            self.save_json_to_file(f'{profile_dir}/personal-information', self.garth.connectapi(f'{self.garmin_connect_user_profile_url}/personal-information'))

        self.display_name = self.social_profile['displayName']
        self.full_name = self.social_profile['fullName']
        print("succesful login: %s (%s)", self.full_name, self.display_name)
        return True

    @classmethod
    def __convert_to_json(cls, object):
        return object.__str__()

    @classmethod
    def save_json_to_file(cls, filename, json_data, overwite=False):
        """Save JSON formatted data to a file."""
        full_filename = f'{filename}.json'
        exists = os.path.isfile(full_filename)
        if not exists or overwite:
            print("%s %s", 'Overwriting' if exists else 'Saving', full_filename)
            with open(full_filename, 'w') as file:
                file.write(json.dumps(json_data, default=cls.__convert_to_json))
                return full_filename

    def __get_summary_day(self, date):
        print("get_summary_day: %s", date)
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
            print("Exception getting daily summary: %s", e)

    def get_daily_summaries(self, date, days):
        """Download the daily summary data from Garmin Connect and save to a JSON file."""
        print("Getting daily summaries: %s (%d)", date, days)
        step_days = []
        for day in tqdm(range(0, days), unit='days'):
            download_date = date + datetime.timedelta(days=day)
            file_path = self.__get_summary_day( download_date)
            step_days.append(file_path)
            # Sleep for between 1 and 2 seconds to avoid getting blocked by Garmin
            # for too many requests.
            if days > 3:
                time.sleep(1 + random.random())
        return step_days



    
