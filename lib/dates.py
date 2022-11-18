import datetime

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
		end_of_year = datetime.date(year=year, month=12, day=31)
		start_date = join_date if join_date > start_of_year else start_of_year
		date_ranges.append((start_date, end_of_year))
		year = year - 1
	return date_ranges