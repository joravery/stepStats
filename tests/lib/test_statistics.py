import pytest
import datetime
from lib.statistics import Statistics
from lib.day import Day
import random

STEP_GOAL=5000

def test_day_requires_data(match=r"Cannot analyze statistics without any days"):
    with pytest.raises(TypeError):
        Statistics()

def test_day_requires():
    day = get_single_valid_day()
    stats = Statistics([day], step_goal=STEP_GOAL)
    stats.calculate_stats()

def test_find_maximum_streak():
    streak_length = random.randrange(0, 1000)
    (days, expected_steps, expected_end) = get_streak(streak_days=streak_length)
    stats = Statistics(days, step_goal=STEP_GOAL)
    
    (max_streak, streak_step, streak_end) = stats.find_maximum_streak()
    
    assert(max_streak == streak_length)
    assert(streak_step == expected_steps)
    assert(streak_end == expected_end)

def test_find_maximum_streak_in_progress():
    streak_length = random.randrange(0, 1000)
    (days, expected_steps, expected_end) = get_streak(streak_days=streak_length, after_days=0)
    stats = Statistics(days, step_goal=STEP_GOAL)
    
    (max_streak, streak_step, streak_end) = stats.find_maximum_streak()
    
    assert(max_streak == streak_length)
    assert(streak_step == expected_steps)
    assert(streak_end == expected_end)

def test_find_maximum_streak_only_streak_days():
    streak_length = random.randrange(0, 1000)
    (days, expected_steps, expected_end) = get_streak(before_days=0, streak_days=streak_length, after_days=0)
    stats = Statistics(days, step_goal=STEP_GOAL)
    
    (max_streak, streak_step, streak_end) = stats.find_maximum_streak()
    
    assert(max_streak == len(days))
    assert(max_streak == streak_length)
    assert(streak_step == expected_steps)
    assert(streak_end == expected_end)

def test_find_maximum_streak_no_streak():
    streak_length = 0
    (days, expected_steps, _) = get_streak(before_days=100, streak_days=streak_length)
    stats = Statistics(days, step_goal=STEP_GOAL)
    
    (max_streak, streak_step, streak_end) = stats.find_maximum_streak()
    
    assert(max_streak == streak_length)
    assert(streak_step == expected_steps)
    assert(streak_end == '')

def get_streak(before_days=random.randrange(1,100), streak_days=0, after_days=random.randrange(1,100)):
    days = []
    end_date = None
    steps = 0
    date = datetime.date(year=2019, month=1, day=1)
    for i in range(0, before_days):
        days.append(get_single_valid_day(steps=random.randrange(1, STEP_GOAL), date=date))
        date = date + datetime.timedelta(days=1)

    for i in range(0, streak_days):
        streak_day = get_single_valid_day(steps=random.randrange(STEP_GOAL, 20*STEP_GOAL), date=date)
        steps += streak_day.steps
        days.append(streak_day)
        date = date + datetime.timedelta(days=1)

    end_date = date - datetime.timedelta(days=1)
    for i in range(0, after_days):
        days.append(get_single_valid_day(steps=random.randrange(1, STEP_GOAL), date=date))

    return (days, steps, end_date)

def get_single_valid_day(steps: int=1234, date: datetime.date=datetime.date(year=2021, month=10, day=11)):
    return Day({"value": steps, "dateTime": f"{date.year}-{date.month}-{date.day}"})