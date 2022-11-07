import pytest
from lib.day import Day

def test_day_requires_data():
    with pytest.raises(TypeError):
        Day()

