#import matplotlib.pyplot as plt
import pprint as pp
import fitbit
import json
import math
# from gather_keys_oauth2 import OAuth2Server

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

# server = OAuth2Server(CLIENT_ID, CLIENT_SECRET)
# authorize_response = server.browser_authorize()

# for key, value in server.fitbit.client.session.token.items():
# 	print('{} = {}'.format(key, value))
# ACCESS_TOKEN = server.fitbit.client.session.token["access_token"]
# REFRESH_TOKEN = server.fitbit.client.session.token["refresh_token"]

print(f"AccessToken: {ACCESS_TOKEN}")
print(f"RefreshToken: {REFRESH_TOKEN}")

oauthClient = fitbit.FitbitOauth2Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN, refresh_cb=save_updated_credentials)
token_refresh_output = oauthClient.refresh_token()
save_updated_credentials(token_refresh_output)
REFRESH_TOKEN = token_refresh_output["refresh_token"]
ACCESS_TOKEN = token_refresh_output["access_token"]

auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)

steps = {"days": [], "month": {}, "year": {}}
start_date = datetime.date.today()

# should replace pd call with datetime call, but by default datetime.datetime doesn't work with 'yyyy-mm-dd'
join_date = datetime.datetime.strptime(get_user_joined_date(auth2_client), "%Y-%m-%d").date()

print(f"Join date: {join_date}")
while start_date > join_date:
	one_year_ago = datetime.date(year=start_date.year-1, month=start_date.month, day=start_date.day)
	end_date = join_date if join_date > one_year_ago else one_year_ago
	try:
		one_year = auth2_client.time_series("activities/steps", end_date=end_date, base_date=start_date)
	except Exception as e:
		print(f"Error when getting steps for {end_date} to {start_date}")
	
	# Bug here if start_date is at start of month (or close to it)
	start_date = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day-1).date()
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
print(f"Longest streak is {max_streak:,} days, ended on {streak_end} and had a total of {streak_steps:,} steps for an average of {int(streak_steps/max_streak):,} per day!")
pp.pprint(f"Top ten days all-time")
pp.pprint(sorted(steps['days'], key=lambda k: k.all_time_rank)[:10])
