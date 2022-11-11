import pprint as pp
import fitbit
import json
from multiprocessing.pool import ThreadPool as Pool

from lib.day import Day
from lib.statistics import Statistics
from lib import client_helper
import datetime
import time

start_time = time.time()

def save_updated_credentials(response):
	ACCESS_TOKEN = response["access_token"]
	REFRESH_TOKEN = response["refresh_token"]	
	with open("./credentials.json", "r+") as credFile:
		cred_dict = json.load(credFile)
		cred_dict["access_token"] = ACCESS_TOKEN
		cred_dict["refresh_token"] = REFRESH_TOKEN
		credFile.seek(0)
		credFile.write(json.dumps(cred_dict))

time_to_creds = time.time() - start_time
print(f"Time before loading creds: {time_to_creds:.2f}")
try: 
	with open("./credentials.json", "r+") as credFile:
		cred_dict = json.load(credFile)
		CLIENT_ID = cred_dict["client_id"]
		CLIENT_SECRET = cred_dict["client_secret"]
		ACCESS_TOKEN = cred_dict["access_token"]
		REFRESH_TOKEN = cred_dict["refresh_token"] 
except Exception as e:
	print(dir(e))
	print(e.msg)
	print("Unable to load credentials")
	exit()

time_after_creds = time.time() - start_time
print(f"Time spent loading creds: {time_after_creds - time_to_creds:.2f}")

oauthClient = fitbit.FitbitOauth2Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN, refresh_cb=save_updated_credentials)
time_after_client = time.time() - start_time
print(f"Time spent creating OAuth2Client: {time_after_client - time_after_creds:.2f}")
token_refresh_output = oauthClient.refresh_token()
time_after_token_refresh = time.time() - start_time
print(f"Time spent creating client: {time_after_token_refresh - time_after_client:.2f}")
token_refresh_output = oauthClient.refresh_token()
time_after_token_refresh = time.time() - start_time
print(f"Time spent saving updated creds: {time_after_token_refresh - time_after_client:.2f}")

save_updated_credentials(token_refresh_output)
time_after_token_saving = time.time() - start_time
print(f"Time spent saving updated creds: {time_after_token_saving - time_after_token_refresh:.2f}")

REFRESH_TOKEN = token_refresh_output["refresh_token"]
ACCESS_TOKEN = token_refresh_output["access_token"]

auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

# Should move to utility file with tests
def get_start_end_dates(join_date: datetime.date):
	start_date = datetime.date.today()
	# Get to start of current year, then get each year prior
	date_ranges = []
	date_ranges.append(get_current_year_range(start_date=start_date))
	date_ranges = date_ranges + get_all_prior_years(start_date=start_date, join_date=join_date)
	return date_ranges

def get_current_year_range(start_date: datetime.date):
	start_of_year = datetime.date(year=start_date.year, month=1, day=1)
	return (start_of_year, start_date)

def get_all_prior_years(start_date: datetime.date, join_date:datetime.date):
	date_ranges = []
	year = start_date.year - 1
	while year >= join_date.year:
		start_of_year = datetime.date(year=year, month=1, day=1)
		end_of_year = datetime.datetime(year=year, month=12, day=31)
		start_date = join_date if join_date > start_of_year else start_of_year
		date_ranges.append((start_date, end_of_year))
		year = year - 1
	return date_ranges

steps = {"days": [], "month": {}, "year": {}}
time_before_joined_date = time.time() - start_time
join_date = datetime.datetime.strptime(client_helper.get_user_joined_date(auth2_client), "%Y-%m-%d").date()
time_after_joined_date = time.time() - start_time
print(f"Time spent getting join date: {time_after_joined_date - time_before_joined_date:.2f}")

def get_steps_by_date_range(args:tuple=None):
	end_date=args[0]
	start_date=args[1]
	auth2_client = args[2]
	try:
		return auth2_client.time_series("activities/steps", end_date=end_date, base_date=start_date)
	except Exception as e:
		print(f"Error when getting steps for {end_date} to {start_date}")

print(f"Join date: {join_date}")
date_ranges = get_start_end_dates(join_date)

# maybe find a better way to pass the client?
bad_args = [(x[0], x[1], auth2_client) for x in date_ranges]
pool = Pool(processes=len(date_ranges))
day_responses = pool.map(get_steps_by_date_range, bad_args)
for day_response in day_responses:
	steps['days'] += [Day(x) for x in day_response['activities-steps']]

time_after_step_data = time.time() - start_time
print(f"Time spent getting step data: {time_after_step_data - time_after_joined_date:.2f}")
steps["days"] = sorted(steps["days"])
stats = Statistics(steps["days"])



time_after_calculations = time.time() - start_time
print(f"Time spent calculating: {time_after_calculations - time_after_step_data:.2f}")

print("Last 10 days: ")
pp.pprint(stats.get_most_recent_days())
print(f"Total entries: {len(steps['days']):,}")
print(f"Step total from accumulate dict: {sum(entry.steps for entry in steps['days']):,}")
(max_streak, streak_steps, streak_end) = stats.find_maximum_streak()
if streak_end == datetime.date.today()- datetime.timedelta(days=1) or streak_end == datetime.date.today():
	print(f"Longest streak is {max_streak:,} days and is still in progress with {streak_steps:,} total steps for an average of {int(streak_steps/max_streak):,} per day!")
else:
	print(f"Longest streak is {max_streak:,} days, ended on {streak_end} and had a total of {streak_steps:,} steps for an average of {int(streak_steps/max_streak):,} per day!")
pp.pprint(f"Top ten days all-time")
pp.pprint(sorted(steps['days'], key=lambda k: k.all_time_rank)[:10])

print(f"Total time: {time.time() - start_time:.2f}")
