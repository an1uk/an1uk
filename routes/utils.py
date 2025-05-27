import re
import os
import boto3
from botocore.exceptions import ClientError
from flask import current_app

BUCKET_NAME = os.getenv('S3_BUCKET')
PREFIX = os.getenv('S3_PREFIX')

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

def list_s3_keys(bucket, prefix):
    try:
        paginator = s3.get_paginator('list_objects_v2')
        return [obj['Key'] for page in paginator.paginate(Bucket=bucket, Prefix=prefix) for obj in page.get('Contents', [])]
    except ClientError as e:
        current_app.logger.error(f"S3 access error: {e.response['Error']['Message']}")
        return []

def extract_sku_from_key(key):
    m = re.match(r'items\/(\d{2})\/(\d{2})\/(\d{2})(?:\/|$)', key)
    return ''.join(m.groups()) if m else None

