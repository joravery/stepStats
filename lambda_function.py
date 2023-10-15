import json
import datetime

import jsonpickle
import os

from util.day import Day
from util.statistics import Statistics
from util.credentials.aws_lambda import AWSLambdaCredentials
from util.compression import compress_string
from util.steps_file import get_current_file_from_s3, upload_compressed_steps_to_s3
from util.garmin_get import garmin_get_steps_since_last_date

STEPS_FILE_NAME = os.environ['steps_file_name']
WEBSITE_BUCKET_NAME = os.environ['public_bucket_name']
SECURE_BUCKET_NAME = os.environ['secure_bucket_name']

def lambda_handler(event, context):
    steps = get_current_file_from_s3(SECURE_BUCKET_NAME, STEPS_FILE_NAME)
    username, password = AWSLambdaCredentials().get_credentials()

    # Assumes steps is sorted already by date
    yesterday = datetime.datetime.strptime(steps[-2]["date"], "%Y-%m-%d").date()
    print(f"Last date in current steps: {yesterday}")
    
    new_steps = get_steps_since_last_date(yesterday, username, password)
    steps = merge_steps(steps, new_steps)
    upload_compressed_steps_to_s3(compress_string(str(jsonpickle.encode(steps, unpicklable=False))), SECURE_BUCKET_NAME, STEPS_FILE_NAME)
    
    steps, stats = get_steps_stats([Day(x) for x in steps])
    (max_streak, streak_steps, streak_end) = stats.find_maximum_streak()
    if streak_end == datetime.date.today()- datetime.timedelta(days=1) or streak_end == datetime.date.today():
        print(f"Longest streak is {max_streak:,} days and is still in progress with {streak_steps:,} total steps for an average of {int(streak_steps/max_streak):,} per day!")
    else:
        print(f"Longest streak is {max_streak:,} days, ended on {streak_end} and had a total of {streak_steps:,} steps for an average of {int(streak_steps/max_streak):,} per day!")
    total_days = len(stats.days)
    print(f"Total days: {total_days:,}. Steps all-time: {stats.all_time_steps:,}. Average steps/day: {int(stats.all_time_steps/total_days):,}.")

    stats_metadata = build_metadata_from_stats(stats)
    compressed_json = prepare_json(steps, stats_metadata)

    upload_compressed_steps_to_s3(compressed_json, WEBSITE_BUCKET_NAME, STEPS_FILE_NAME)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def merge_steps(steps, new_steps) -> list:
    ### Inefficient, but it works ... for shame
    for day in new_steps:
        if day["date"] not in [x["date"] for x in steps]:
            steps.append(day)
        elif day["date"] in [x["date"] for x in steps]:
            for i, step in enumerate(steps):
                if step["date"] == day["date"] and step["steps"] < day["steps"]:
                    steps[i] = day
    return steps

def get_steps_since_last_date(start_date, username, password) -> list:
        steps = garmin_get_steps_since_last_date(start_date, username, password)
        print(steps)
        return steps

def get_steps_stats(steps) -> tuple:
    steps = sorted(steps)
    stats = Statistics(steps)
    return steps, stats

def build_metadata_from_stats(stats: Statistics) -> dict:
    metadata = {}
    metadata["all_time_steps"] = stats.all_time_steps
    metadata["all_time_days"] = len(stats.days)
    metadata["all_time_average"] = stats.all_time_average
    metadata["months"] = stats.months
    metadata["years"] = stats.years

    return metadata
    
def prepare_json(steps, metadata) -> bytes:
    data = {"stats": metadata, "days": steps}
    data_json = str(jsonpickle.encode(data, unpicklable=False))
    return compress_string(data_json)

    

if __name__ == "__main__":
    lambda_handler(None, None)
