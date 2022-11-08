import pytest
import datetime
from lib.day import Day

def test_day_requires_data():
    with pytest.raises(TypeError):
        Day()

def test_day_requires_step_value():
    with pytest.raises(KeyError, match=r"value"):
        Day({"dateTime": "2022-02-02"})

def test_day_requires_date_time():
    with pytest.raises(KeyError, match=r"dateTime"):
        Day({"value": 1234})

def test_valid_input_initializes_defaults():
    value = 123
    new_day = Day({"value": value, "dateTime": "2022-10-12"})
    assert(new_day.all_time_rank == -1)
    assert(new_day.top_percentile == -1)
    assert(new_day.steps == value)
    assert(new_day.date < datetime.date.today())