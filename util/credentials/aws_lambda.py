import os
import boto3
import jsonpickle

SECURE_BUCKET_NAME = os.environ['secure_bucket_name']
CRED_FILE_NAME = os.environ['credential_file_name']


class AWSLambdaCredentials:
    def __init__(self) -> None:
        self.s3 = boto3.client("s3")

    def get_credentials(self):
        try:
            picked_creds = self.s3.get_object(Bucket=SECURE_BUCKET_NAME, Key=CRED_FILE_NAME)["Body"].read()
            creds = jsonpickle.decode(picked_creds)
            USERNAME = creds["credentials"]["user"]
            PASSWORD = creds["credentials"]["password"]
            return (USERNAME, PASSWORD)
        except Exception as e:
            print(f"Unable to get credentials file from S3! {e}")
            raise e
