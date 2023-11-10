import garth
from garth.exc import GarthHTTPError

"""Class for downloading step data from Garmin Connect."""


class Download:
    """Class for downloading health data from Garmin Connect"""

    def __init__(self, tokens=None):
        """Create a new Download class instance."""
        self.display_name = ""
        self.full_name = ""
        self.garth = garth.Client()
        self.garth.loads(tokens)
        self.original_tokens_expires = self.garth.oauth2_token.expires_at

    def login(self) -> tuple:
        """Login to Garmin Connect."""
        try:
            self.display_name = self.garth.profile['displayName']
            self.full_name = self.garth.profile['fullName']
            return self.full_name, self.display_name
        except GarthHTTPError as e:
            print(f"failed to login, likely need to refresh oath1 token {e}")
            return None, None

    def get_daily_summaries(self, end_date, num_days) -> list:
        step_days = garth.stats.DailySteps.list(end_date, num_days, client=self.garth)
        return [{"date": str(day.calendar_date), "steps": day.total_steps} for day in step_days]

    def check_for_refreshed_tokens(self) -> (bool, str):
        if self.original_tokens_expires != self.garth.oauth2_token.expires_at:
            return True, self.garth.dumps()
        else:
            return False, None
