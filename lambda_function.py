import datetime
import json
import os

import jsonpickle

from util.compression import compress_string
from util.credentials.aws_lambda import AWSLambdaCredentials
from util.day import Day
from util.garmin_download import Download
from util.statistics import Statistics
from util.steps_file import get_compressed_file_from_s3, upload_compressed_file_to_s3

STEPS_FILE_NAME = os.environ['steps_file_name']
WEBSITE_BUCKET_NAME = os.environ['public_bucket_name']
SECURE_BUCKET_NAME = os.environ['secure_bucket_name']


def lambda_handler(event, context):
    steps = get_compressed_file_from_s3(SECURE_BUCKET_NAME, STEPS_FILE_NAME)
    creds = AWSLambdaCredentials()
    _, _, tokens = creds.get_credentials()
    summary = {"tokens_updated": False, "steps_updated": False}

    steps = sorted(steps, key=lambda x: x["date"])
    new_steps = get_steps_update_garmin_creds(creds, tokens, summary)
    steps, updated = merge_steps(steps, new_steps)

    # If there were no new steps, we don't need to update anything
    if not updated:
        return success(summary)
    summary["steps_updated"] = True

    # Store just the steps and dates in the secure bucket for later usage
    upload_compressed_file_to_s3(compress_string(str(jsonpickle.encode(steps, unpicklable=False))), SECURE_BUCKET_NAME,
                                 STEPS_FILE_NAME)

    # Now calculate stats and store them in the public bucket for the website to use
    steps, stats = get_steps_stats([Day(x) for x in steps if x['date'] and x['steps']])
    add_streak_to_summary(stats, summary)
    add_all_time_stats_to_summary(stats, summary)
    stats_metadata = build_metadata_from_stats(stats)
    compressed_json = prepare_json(steps, stats_metadata)

    upload_compressed_file_to_s3(compressed_json, WEBSITE_BUCKET_NAME, STEPS_FILE_NAME)

    return success(summary)


def add_all_time_stats_to_summary(stats, summary):
    summary["all_time_steps"] = f"{stats.all_time_steps:,}"
    summary["all_time_days"] = f"{len(stats.days):,}"
    summary["all_time_average"] = f"{stats.all_time_average:,}"


def add_streak_to_summary(stats, summary):
    max_streak, streak_steps, streak_end = stats.find_maximum_streak()
    summary["longest_streak"] = f"{max_streak:,}"
    summary["longest_streak_steps"] = f"{streak_steps:,}"
    summary["longest_streak_average_steps"] = f"{streak_steps // max_streak:,}"
    summary["longest_streak_current_streak"] = True
    if not (streak_end == datetime.date.today() - datetime.timedelta(days=1) or streak_end == datetime.date.today()):
        summary["longest_streak_current_streak"] = False
        summary["longest_streak_end"] = str(streak_end)


def success(message):
    if os.getenv('PRINT_SUMMARY') is not None:
        print(json.dumps(message))
    return {'statusCode': 200, 'body': json.dumps(message)}


def merge_steps(steps, new_steps) -> tuple:
    updated = False
    if steps is None or new_steps is None:
        return [], updated
    for new_day in new_steps:
        if missing_fields(new_day):
            continue
        for existing_day in steps[::-1]:
            if existing_day["date"] == new_day["date"]:
                if should_update_step_count(existing_day, new_day):
                    existing_day["steps"] = new_day["steps"]
                    updated = True
                break
            elif new_day["date"] > existing_day["date"]:
                steps.append(new_day)
                updated = True
                break
    return steps, updated


def should_update_step_count(existing_day, new_day) -> bool:
    return existing_day["steps"] is None or new_day["steps"] > existing_day["steps"]


def missing_fields(day) -> bool:
    return day["date"] is None or day["steps"] is None


def get_steps_update_garmin_creds(creds, tokens, summary) -> list:
    start_date = datetime.date.today()
    num_days = 2
    res = get_steps_since_date(start_date, num_days, tokens, summary)
    if res["needs_update"]:
        summary["Tokens updated"] = True
        creds.save_credentials(res["new_tokens"])
    return res["steps"]


def get_steps_since_date(end_date, num_days, tokens, summary):
    download = Download(tokens=tokens)
    name, garmin_id = download.login()
    if name is None or garmin_id is None:
        summary["Login error"] = True
    summary["Display name"] = name
    summary["Garmin id"] = garmin_id
    summary["Days to download"] = num_days
    summary["End date"] = str(end_date)

    step_days = download.get_daily_summaries(end_date, num_days)
    needs_update, new_tokens = download.check_for_refreshed_tokens()
    return {"steps": step_days, "needs_update": needs_update, "new_tokens": new_tokens}


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
