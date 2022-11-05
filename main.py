import pprint as pp
from xmlrpc.client import DateTime
import fitbit
import json
import math

from lib.day import Day
import pandas as pd 
import datetime

def get_user_joined_date(client):
	try:
		user_profile = client.user_profile_get()
	except Exception as e:
		print("Unable to get user profile from client")
		raise e
	try:
		return user_profile['user']['memberSince']
	except Exception as e:
		print("User profile from API missing either 'user' or 'memberSince' keys")
		raise e

def calculate_percent_at_goal(steps, goal=5000):
	for month in steps["month"]:
		steps["month"][month]["goal_percent"] = float(steps["month"][month]["goal_days"]/steps["month"][month]["days"] * 100)

	for year in steps["year"]:
		steps["year"][year]["goal_percent"] = float(steps["year"][year]["goal_days"]/steps["year"][year]["days"] * 100)

def calculate_averages(steps):
	for month in steps["month"]:
		steps["month"][month]["daily_average_steps"] = int(steps["month"][month]["steps"]/steps["month"][month]["days"])

	for year in steps["year"]:
		steps["year"][year]["daily_average_steps"] = int(steps["year"][year]["steps"]/steps["year"][year]["days"])

def calculate_daily_rank(steps):
	step_sorted = sorted(steps["days"], key=lambda k: k.steps, reverse=True)
	for i in range(0, len(step_sorted)):
		step_sorted[i].all_time_rank = i+1
		step_sorted[i].top_percentile = i/len(step_sorted) * 100
	# default object comparators will sort by date
	steps["days"] = sorted(step_sorted)

def calculate_sums(steps, goal=5000):
	for day in steps["days"]:
		year, month = (day.date.year, day.date.month)
		add_to_totals(steps, year, month, day.steps, goal)

def add_to_totals(steps, year, month, daily_step_count, goal):
	add_to(daily_step_count, year, daily_step_count>goal)
	add_to(daily_step_count, year, daily_step_count>goal, month=month)

def add_to(daily_step_count, year, goal_met, month=None):
	granularity = "year" if month is None else "month"
	key = f"{year}" if month is None else f"{year}-{month}"
	
	if key not in steps[granularity]:
		steps[granularity][key]={"steps": 0, "days": 0, "goal_days": 0}
	
	steps[granularity][key]["steps"] += daily_step_count
	steps[granularity][key]["days"] += 1
	if goal_met:
		steps[granularity][key]["goal_days"] += 1

def calculate_streak_per_year(steps, goal):
	pass

def find_maximum_streak(steps, goal=5000):
	def is_bigger_streak(current_streak, max_streak, current_steps, max_steps):
		if current_streak > max_streak:
			return True
		if current_streak == max_streak and current_steps > streak_steps:
			return True
		return False
	max_streak = 0
	streak_steps = 0
	streak_end = ''
	current_streak = 0
	current_steps = 0

	for i in range(0, len(steps['days'])):
		day_steps = int(steps['days'][i].steps)
		if day_steps >= goal:
			current_streak += 1
			current_steps += day_steps
			if is_bigger_streak(current_streak, max_streak, current_steps, streak_steps):
				max_streak = current_streak
				streak_steps = current_steps
				streak_end = steps['days'][i].date if i > 0 else ''
		else:	
			current_streak = 0
			current_steps = 0
	return (max_streak, streak_steps, streak_end)

def save_updated_credentials(response):
	ACCESS_TOKEN = response["access_token"]
	REFRESH_TOKEN = response["refresh_token"]	
	with open("./credentials.json", "r+") as credFile:
		cred_dict = json.load(credFile)
		cred_dict["access_token"] = ACCESS_TOKEN
		cred_dict["refresh_token"] = REFRESH_TOKEN
		credFile.seek(0)
		credFile.write(json.dumps(cred_dict))

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

oauthClient = fitbit.FitbitOauth2Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN, refresh_cb=save_updated_credentials)
token_refresh_output = oauthClient.refresh_token()
save_updated_credentials(token_refresh_output)
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
# should replace pd call with datetime call, but by default datetime.datetime doesn't work with 'yyyy-mm-dd'
join_date = datetime.datetime.strptime(get_user_joined_date(auth2_client), "%Y-%m-%d").date()
date_ranges = get_start_end_dates(join_date)
print(f"Join date: {join_date}")
for date_range in date_ranges:
	end_date=date_range[0]
	start_date=date_range[1]
	try:
		one_year = auth2_client.time_series("activities/steps", end_date=end_date, base_date=start_date)
	except Exception as e:
		print(f"Error when getting steps for {end_date} to {start_date}")
	steps['days'] += [Day(x) for x in one_year['activities-steps']]

steps["days"] = sorted(steps["days"])
calculate_sums(steps)
calculate_averages(steps)
calculate_percent_at_goal(steps)
calculate_daily_rank(steps)

# pp.pprint(steps["days"])
# pp.pprint(steps["month"])
# pp.pprint(steps["year"])
print(f"Total entries: {len(steps['days']):,}")
print(f"Step total from accumulate dict: {sum(entry.steps for entry in steps['days']):,}")
(max_streak, streak_steps, streak_end) = find_maximum_streak(steps)
if streak_end == datetime.date.today()- datetime.timedelta(days=1) or streak_end == datetime.date.today():
	print(f"Longest streak is {max_streak:,} days and is still in progress with {streak_steps:,} total steps for an average of {int(streak_steps/max_streak):,} per day!")
else:
	print(f"Longest streak is {max_streak:,} days, ended on {streak_end} and had a total of {streak_steps:,} steps for an average of {int(streak_steps/max_streak):,} per day!")
pp.pprint(f"Top ten days all-time")
pp.pprint(sorted(steps['days'], key=lambda k: k.all_time_rank)[:10])
