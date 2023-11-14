# This script is used to refresh the oauth1 credentials for garmin connect
# The oauth1 token is good for 1 year, so this script should be run at least once a year
# It is used by garth to refresh the oauth2 credentials when they expire
import garth

from util.credentials.aws_lambda import AWSLambdaCredentials


def update_garmin_creds():
    creds = AWSLambdaCredentials()
    username, password, tokens = creds.get_credentials()
    garth.login(username, password)
    print(f"Uploading new tokens to S3...")
    updated_tokens = garth.client.dumps()
    creds.save_credentials(updated_tokens)


if __name__ == "__main__":
    update_garmin_creds()
