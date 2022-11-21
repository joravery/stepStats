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


def get_steps_by_date_range(args:tuple=None):
	if args is None:
		raise Error("Must past tuple containing start, end, and client")
	end_date=args[0]
	start_date=args[1]
	auth2_client = args[2]
	try:
		return auth2_client.time_series("activities/steps", end_date=end_date, base_date=start_date)
	except Exception as e:
		print(f"Error when getting steps for {end_date} to {start_date}")