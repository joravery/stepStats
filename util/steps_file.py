import boto3
import jsonpickle

from util.compression import decompress_string


def get_compressed_file_from_s3(bucket, key):
    try:
        s3 = boto3.client('s3')
        pickled_steps = s3.get_object(
            Bucket=bucket,
            Key=key
        )['Body'].read()
    except Exception as e:
        print(f"Error when getting steps from s3: {e}")
        return None
    try:
        return jsonpickle.decode(decompress_string(pickled_steps))
    except Exception as e:
        print(f"Error when decoding steps from s3: {e}")
        return None


def upload_compressed_file_to_s3(json_bytes, bucket, key) -> None:
    s3 = boto3.client('s3')
    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json_bytes,
            ContentEncoding="br",
            Metadata={
                "Content-Encoding": "br",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        print(f"Error when uploading {key} to {bucket}: {e}")
        return None


if __name__ == "__main__":
    print(get_compressed_file_from_s3())
