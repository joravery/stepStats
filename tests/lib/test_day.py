import pytest
import datetime as date
from util.day import Day

def test_day_requires_data():
    with pytest.raises(TypeError):
        Day()

def test_day_requires_step_value():
    with pytest.raises(KeyError, match=r"steps"):
        Day({"date": "2022-02-02"})

def test_day_requires_date_time():
    with pytest.raises(KeyError, match=r"date"):
        Day({"steps": 1234})

def test_valid_input_initializes_defaults():
    value = 123
    new_day = Day({"steps": value, "date": "2022-10-12"})
    assert(new_day.all_time_rank == -1)
    assert(new_day.top_percentile == -1)
    assert(new_day.steps == value)
    assert(new_day.date < date.date.today())

def test_date_comaprator():
    value = 123
    first_day = Day({"steps": value, "date": "2022-10-12"})
    second_day = Day({"steps": value, "date": "2022-10-13"})
    assert( first_day < second_day and second_day > first_day )

def test_comaprator_equal():
    value = 123
    first_day = Day({"steps": value, "date": "2022-10-13"})
    second_day = Day({"steps": value, "date": "2022-10-13"})
    assert( first_day == second_day)



expected_digits = [(1, "1st"), (2, "2nd"), (3, "3rd"), (4, "4th"), (10, "10th"), (11, "11th"), (21, "21st")]
@pytest.mark.parametrize("digit,expected_ordinality_string", expected_digits)
def test_ordinality(digit, expected_ordinality_string):
    print(f"digit: {digit}, expected_ordinality_string: {expected_ordinality_string}")
    test_day = Day({"steps": 123, "date": "2022-10-13"})
    test_day.all_time_rank = digit
    assert(expected_ordinality_string in repr(test_day) )
