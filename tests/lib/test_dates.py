import datetime
from util.dates import *

def test_same_year_returns_one_range():
    today = datetime.date.today()
    join_date = datetime.date(year=today.year, month=1, day=1)
    
    date_ranges = get_start_end_dates(join_date)
    
    assert(len(date_ranges) == 1)

def test_prior_year_returns_two_ranges():
    today = datetime.date.today()
    join_date = datetime.date(year=today.year-1, month=3, day=6)
    
    date_ranges = get_start_end_dates(join_date)
    
    assert(len(date_ranges) == 2)

def test_earliest_range_end_on_join_date():
    today = datetime.date.today()
    start_year = today.year - 1
    start_month = 3
    start_day = 1
    join_date = datetime.date(year=start_year, month=start_month, day=start_day)
    
    date_ranges = get_start_end_dates(join_date)
    
    earliest_range = date_ranges[-1]
    assert(earliest_range[0].year == start_year)
    assert(earliest_range[0].month == start_month)
    assert(earliest_range[0].day == start_day)

def test_ranges_descending_order():
    today = datetime.date.today()
    join_date = datetime.date(year=today.year-1, month=3, day=6)
    
    date_ranges = get_start_end_dates(join_date)
    
    assert(len(date_ranges) == 2)

    for i in range(len(date_ranges) - 1):
        assert( date_ranges[i][0] > date_ranges[i+1][0] )
        assert( date_ranges[i][1] > date_ranges[i+1][1] )
