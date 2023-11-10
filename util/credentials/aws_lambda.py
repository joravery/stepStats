import os

import boto3
import jsonpickle

SECURE_BUCKET_NAME = os.environ['secure_bucket_name']
CRED_FILE_NAME = os.environ['credential_file_name']


class AWSLambdaCredentials:
    def __init__(self) -> None:
        self.s3 = boto3.client("s3")
        self.creds = None

    def get_credentials(self) -> tuple:
        try:
            picked_creds = self.s3.get_object(Bucket=SECURE_BUCKET_NAME, Key=CRED_FILE_NAME)["Body"].read()
            self.creds = jsonpickle.decode(picked_creds)
            username = self.creds["credentials"]["user"]
            password = self.creds["credentials"]["password"]
            tokens = self.creds["credentials"]["tokens"]
            return username, password, tokens
        except Exception as e:
            print(f"Unable to get credentials file from S3! {e}")
            raise e

    def save_credentials(self, new_tokens: str) -> None:
        self.creds["credentials"]["tokens"] = new_tokens
        try:
            self.s3.put_object(Bucket=SECURE_BUCKET_NAME, Key=CRED_FILE_NAME,
                               Body=jsonpickle.encode(self.creds, unpicklable=False))
        except Exception as e:
            print(f"Unable to save credentials file to S3! {e}")
            raise e
