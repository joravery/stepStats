import datetime
import json
import os

import jsonpickle

from util.compression import compress_string
from util.credentials.aws_lambda import AWSLambdaCredentials
from util.day import Day
from util.garmin_get import get_steps_since_date
from util.statistics import Statistics
from util.steps_file import get_compressed_file_from_s3, upload_compressed_file_to_s3

STEPS_FILE_NAME = os.environ['steps_file_name']
WEBSITE_BUCKET_NAME = os.environ['public_bucket_name']
SECURE_BUCKET_NAME = os.environ['secure_bucket_name']


def lambda_handler(event, context):
    steps = get_compressed_file_from_s3(SECURE_BUCKET_NAME, STEPS_FILE_NAME)
    creds = AWSLambdaCredentials()
    _, _, tokens = creds.get_credentials()

    steps = sorted(steps, key=lambda x: x["date"])

    new_steps = get_steps_update_garmin_creds(creds, tokens)
    steps = merge_steps(steps, new_steps)
    upload_compressed_file_to_s3(compress_string(str(jsonpickle.encode(steps, unpicklable=False))), SECURE_BUCKET_NAME,
                                 STEPS_FILE_NAME)

    steps, stats = get_steps_stats([Day(x) for x in steps if x['date'] and x['steps']])
    max_streak, streak_steps, streak_end = stats.find_maximum_streak()
    if streak_end == datetime.date.today() - datetime.timedelta(days=1) or streak_end == datetime.date.today():
        print(
            f"Longest streak is {max_streak:,} days and is still in progress with {streak_steps:,} total steps for an "
            f"average of {int(streak_steps / max_streak):,} per day!")
    else:
        print(
            f"Longest streak is {max_streak:,} days, ended on {streak_end} and had a total of {streak_steps:,} steps "
            f"for an average of {int(streak_steps / max_streak):,} per day!")
    total_days = len(stats.days)
    print(
        f"Total days: {total_days:,}. Steps all-time: {stats.all_time_steps:,}."
        f"Average steps/day: {int(stats.all_time_steps / total_days):,}.")

    stats_metadata = build_metadata_from_stats(stats)
    compressed_json = prepare_json(steps, stats_metadata)

    upload_compressed_file_to_s3(compressed_json, WEBSITE_BUCKET_NAME, STEPS_FILE_NAME)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def merge_steps(steps, new_steps) -> list:
    if steps is None or new_steps is None:
        return []
    for new_day in new_steps:
        if missing_fields(new_day):
            continue
        for existing_day in steps[::-1]:
            if existing_day["date"] == new_day["date"]:
                if should_update_step_count(existing_day, new_day):
                    existing_day["steps"] = new_day["steps"]
                break
            elif new_day["date"] > existing_day["date"]:
                steps.append(new_day)
                break
    return steps


def should_update_step_count(existing_day, new_day) -> bool:
    return existing_day["steps"] is None or new_day["steps"] > existing_day["steps"]


def missing_fields(day) -> bool:
    return day["date"] is None or day["steps"] is None


def get_steps_update_garmin_creds(creds, tokens) -> list:
    start_date = datetime.date.today()
    num_days = 2
    res = get_steps_since_date(start_date, num_days, tokens)
    if res["needs_update"]:
        print("Updating credentials")
        creds.save_credentials(res["new_tokens"])
    return res["steps"]


def get_steps_stats(steps) -> tuple:
    steps = sorted(steps)
    stats = Statistics(steps)
    return steps, stats


def build_metadata_from_stats(stats: Statistics) -> dict:
    return {
        "all_time_steps": stats.all_time_steps,
        "all_time_days": len(stats.days),
        "all_time_average": stats.all_time_average,
        "months": stats.months,
        "years": stats.years
    }


def prepare_json(steps, metadata) -> bytes:
    data = {"stats": metadata, "days": steps}
    data_json = str(jsonpickle.encode(data, unpicklable=False))
    return compress_string(data_json)


if __name__ == "__main__":
    lambda_handler(None, None)
