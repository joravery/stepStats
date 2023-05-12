import os
import boto3
import jsonpickle

SECURE_BUCKET_NAME = os.environ['secure_bucket_name']
CRED_FILE_NAME = os.environ['credential_file_name']


class AWSLambdaCredentials:
    def __init__(self) -> None:
        self.s3 = boto3.client("s3")

    def save_updated_credentials(self, response):
        (CLIENT_ID, CLIENT_SECRET, _, _) = self.get_credentials()
        creds = {
            "CLIENT_ID": CLIENT_ID,
            "CLIENT_SECRET": CLIENT_SECRET,
            "ACCESS_TOKEN": response["access_token"],
            "REFRESH_TOKEN": response["refresh_token"],
        }
        pickled_creds = jsonpickle.encode(creds, unpicklable=False)
        self.s3.put_object(Bucket=SECURE_BUCKET_NAME, Key=CRED_FILE_NAME, Body=pickled_creds)

    def get_credentials(self):
        try:
            picked_creds = self.s3.get_object(Bucket=SECURE_BUCKET_NAME, Key=CRED_FILE_NAME)["Body"].read()
            creds = jsonpickle.decode(picked_creds)
            CLIENT_ID = creds["CLIENT_ID"]
            CLIENT_SECRET = creds["CLIENT_SECRET"]
            ACCESS_TOKEN = creds["ACCESS_TOKEN"]
            REFRESH_TOKEN = creds["REFRESH_TOKEN"]
            return (CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN)
        except Exception as e:
            print(f"Unable to get credentials file from S3! {e}")
            raise e
