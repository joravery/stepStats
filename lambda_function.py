import json
import pprint as pp
import fitbit as fitbit
import datetime

import boto3
import jsonpickle
import os
from zoneinfo import ZoneInfo

from util.day import Day
from util.statistics import Statistics
from util import client_helper
from util.credentials.aws_lambda import AWSLambdaCredentials
from util import dates
from util.compression import compress_string

STEPS_FILE_NAME = os.environ['steps_file_name']
WEBSITE_BUCKET_NAME = os.environ['public_bucket_name']


def lambda_handler(event, context):
    auth2_client = get_oauth_client()
    existing_metadata = get_meta_data_from_s3()
    join_date = get_join_date(existing_metadata, auth2_client)
    steps, stats = get_steps(join_date, auth2_client)

    print("Last 10 days: ")
    pp.pprint(stats.get_most_recent_days())
    (max_streak, streak_steps, streak_end) = stats.find_maximum_streak()
    if streak_end == datetime.date.today()- datetime.timedelta(days=1) or streak_end == datetime.date.today():
        print(f"Longest streak is {max_streak:,} days and is still in progress with {streak_steps:,} total steps for an average of {int(streak_steps/max_streak):,} per day!")
    else:
        print(f"Longest streak is {max_streak:,} days, ended on {streak_end} and had a total of {streak_steps:,} steps for an average of {int(streak_steps/max_streak):,} per day!")
    total_days = len(stats.days)
    print(f"Total days: {total_days:,}. Steps all-time: {stats.all_time_steps:,}. Average steps/day: {int(stats.all_time_steps/total_days):,}.")

    stats_metadata = build_metadata_from_stats(stats, existing_metadata)
    compressed_json = prepare_json(steps, stats_metadata)

    print("Uploading to s3 ...")
    upload_steps_to_s3(compressed_json)
    print("Successfully uploaded all files to S3")
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def get_steps(join_date, auth2_client):
    date_ranges = dates.get_start_end_dates(join_date)
    steps = []
    for (start_date, end_date) in date_ranges:
        day_response = client_helper.get_steps_by_date_range((start_date, end_date, auth2_client))
        steps += [Day(x) for x in day_response['activities-steps']]

    steps = sorted(steps)
    today = datetime.datetime.now().astimezone(ZoneInfo("America/Los_Angeles")).date()
    steps = list(filter(lambda day: day.date <= today, steps))
    stats = Statistics(steps)
    return steps, stats

def get_join_date(existing_metadata, auth2_client):
    if "join_date" in existing_metadata:
        join_date = datetime.datetime.strptime(existing_metadata["join_date"], "%Y-%m-%d").date()
    else:
        join_date_string = client_helper.get_user_joined_date(auth2_client)
        join_date = datetime.datetime.strptime(join_date_string, "%Y-%m-%d").date()
        existing_metadata["join_date"] = join_date_string
    return join_date

def get_oauth_client():
    lambda_fitbit_credentials = AWSLambdaCredentials()
    (CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN) = lambda_fitbit_credentials.get_credentials()
    oauthClient = fitbit.FitbitOauth2Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN, refresh_cb=lambda_fitbit_credentials.save_updated_credentials)
    token_refresh_output = oauthClient.refresh_token()
    REFRESH_TOKEN = token_refresh_output["refresh_token"]
    ACCESS_TOKEN = token_refresh_output["access_token"]

    return fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET, oauth2=True, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)

def build_metadata_from_stats(stats: Statistics, existing_metadata: dict) -> dict:
    metadata = {"join_date": existing_metadata["join_date"]}
    
    metadata["all_time_steps"] = stats.all_time_steps
    metadata["all_time_days"] = len(stats.days)
    metadata["all_time_average"] = stats.all_time_average
    metadata["months"] = stats.months
    metadata["years"] = stats.years

    return metadata
    
def prepare_json(steps, metadata):
    data = {"stats": metadata, "days": steps}
    data_json = str(jsonpickle.encode(data, unpicklable=False))
    return compress_string(data_json)


def upload_steps_to_s3(json_bytes, s3_bucket=WEBSITE_BUCKET_NAME):
    s3 = boto3.client('s3')
    print(f"Uploading {STEPS_FILE_NAME} to s3://{s3_bucket}/{STEPS_FILE_NAME}")
    s3.put_object(
        Bucket=s3_bucket,
        Key=STEPS_FILE_NAME,
        Body=json_bytes,
        ContentEncoding="br",
        Metadata={
            "Content-Encoding": "br",
            "Content-Type": "application/json"
        }
    )

def get_meta_data_from_s3():
    try:
        s3 = boto3.client('s3')
        picked_metadata = s3.get_object(
            Bucket=WEBSITE_BUCKET_NAME,
            Key=STEPS_FILE_NAME
        )['Body'].read()
        return jsonpickle.decode(picked_metadata)["stats"]
    except Exception as e:
        print(f"Unable to retrieve metadata from s3: {e}")
        return dict()
    

if __name__ == "__main__":
    lambda_handler(None, None)
