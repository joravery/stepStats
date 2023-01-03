import pprint as pp
import fitbit
import datetime
from multiprocessing.pool import ThreadPool as Pool
import jsonpickle

from lib.day import Day
from lib.statistics import Statistics
from lib import client_helper
from lib.credentials.local import LocalFileCredentials
from lib import dates

CREDENTIAL_FILE_PATH="./credentials.json"
LOCAL_JSON_FILE_PATH="./steps.json"

local_credentials = LocalFileCredentials(CREDENTIAL_FILE_PATH)
(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN) = local_credentials.get_credentials()
oauthClient = fitbit.FitbitOauth2Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN, refresh_cb=local_credentials.save_updated_credentials)
token_refresh_output = oauthClient.refresh_token()
local_credentials.save_updated_credentials(token_refresh_output)
REFRESH_TOKEN = token_refresh_output["refresh_token"]
ACCESS_TOKEN = token_refresh_output["access_token"]

auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

join_date = datetime.datetime.strptime(client_helper.get_user_joined_date(auth2_client), "%Y-%m-%d").date()

date_ranges = dates.get_start_end_dates(join_date)

# maybe find a better way to pass the client?
bad_args = [(x[0], x[1], auth2_client) for x in date_ranges]
pool = Pool(processes=len(date_ranges))
day_responses = pool.map(client_helper.get_steps_by_date_range, bad_args)
steps = []
for day_response in day_responses:
	steps += [Day(x) for x in day_response['activities-steps']]

steps = sorted(steps)
stats = Statistics(steps)
with open(LOCAL_JSON_FILE_PATH, 'w+') as jsonFile:
	jsonFile.write(jsonpickle.encode(steps, unpicklable=False))

meta_data = {"all_time_steps": stats.all_time_steps, "all_time_days": len(stats.days), "all_time_average": stats.all_time_average, "months": stats.months, "years": stats.years}
with open("meta_data.json", 'w+') as jsonFile:
	jsonFile.write(jsonpickle.encode(meta_data, unpicklable=False))

print("Last 10 days: ")
pp.pprint(stats.get_most_recent_days())
(max_streak, streak_steps, streak_end) = stats.find_maximum_streak()
print(f"Top ten days all-time")
pp.pprint(sorted(stats.days, key=lambda k: k.all_time_rank)[:10])
if streak_end == datetime.date.today()- datetime.timedelta(days=1) or streak_end == datetime.date.today():
	print(f"Longest streak is {max_streak:,} days and is still in progress with {streak_steps:,} total steps for an average of {int(streak_steps/max_streak):,} per day!")
else:
	print(f"Longest streak is {max_streak:,} days, ended on {streak_end} and had a total of {streak_steps:,} steps for an average of {int(streak_steps/max_streak):,} per day!")
total_days = len(stats.days)
print(f"Total days: {total_days:,}. Steps all-time: {stats.all_time_steps:,}. Average steps/day: {int(stats.all_time_steps/total_days):,}.")
