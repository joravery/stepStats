### Garmin Data Updater
This repositor is for retrieving my step data from Garmin Connect and updating files in S3 that power my website at https://jordanavery.io

### Overview
The lambda function is triggered by a CloudWatch event. The lambda function will retrieve the step data from Garmin Connect and update the files in S3.
The build script will create a zip file that can be uploaded to AWS Lambda.
An automated build and update of the lambda function is done using GitHub Actions.
As of Oct 15th 2023 Python 3.10 was required (instead of 3.11+) for the brotli compression package to work on AWS Lambda x86_64.

### Credential refresh
The lambda function will refresh the oauth2 token when it expires.
The oauth1 token is currently used to refresh the oauth2 token instead of the refresh token
To update the oauth1 token, run the script:
`python3 scripts/refresh_oauth1_token.py`