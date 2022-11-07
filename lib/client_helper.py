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