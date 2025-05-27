# Consolidated S3 Logic Module: s3/list_files.py

from dotenv import load_dotenv
load_dotenv()
import os
import boto3
from botocore.exceptions import ClientError

# Initialize S3 client using environment variables
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION")
)


def list_s3_keys(bucket: str, prefix: str) -> list:
    """
    List all object keys in an S3 bucket under a specified prefix.

    :param bucket: Name of the S3 bucket
    :param prefix: Prefix path under which to list objects
    :return: List of object key strings
    """
    keys = []
    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            keys.extend(obj.get('Key') for obj in page.get('Contents', []))
    except ClientError as e:
        # Log or print error as appropriate
        print(f"S3 access error: {e.response['Error']['Message']}")
        return []
    return keys