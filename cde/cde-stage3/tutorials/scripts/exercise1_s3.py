"""
Exercise 1: Land the order-event files in S3, via LocalStack.

Run from tutorials\\data, same folder where orders_incoming\\ was created
by generate_dataset.py.

What this script does, in order:
  1. Connects to LocalStack's S3 API (not real AWS)
  2. Creates a bucket called "orders-raw"
  3. Uploads every JSON file in orders_incoming\\ into that bucket
  4. Lists what's now in the bucket, and counts the objects
  5. Downloads one object back and prints it, to prove a round trip works
"""

import json
from pathlib import Path

import boto3

ENDPOINT_URL = "http://localhost:4566"  # LocalStack - never real AWS
BUCKET_NAME = "orders-raw"
LOCAL_FOLDER = Path("orders_incoming")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id="test",   # LocalStack accepts any value here
        aws_secret_access_key="test",
        region_name="us-east-1",
    )


def create_bucket(s3):
    existing = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if BUCKET_NAME in existing:
        print(f"Bucket '{BUCKET_NAME}' already exists - skipping creation.")
    else:
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"Created bucket '{BUCKET_NAME}'.")


def upload_orders(s3):
    files = sorted(LOCAL_FOLDER.glob("order_*.json"))
    if not files:
        raise FileNotFoundError(
            f"No order files found in {LOCAL_FOLDER}\\ - "
            "run generate_dataset.py first."
        )

    for file_path in files:
        key = f"orders_incoming/{file_path.name}"
        s3.upload_file(str(file_path), BUCKET_NAME, key)

    print(f"Uploaded {len(files)} order files to s3://{BUCKET_NAME}/orders_incoming/")


def list_and_count(s3):
    paginator = s3.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="orders_incoming/"):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])

    print(f"\n=== Objects in bucket ({len(keys)} total) ===")
    for key in keys[:5]:
        print(f"  {key}")
    if len(keys) > 5:
        print(f"  ... and {len(keys) - 5} more")

    return keys


def download_one(s3, keys):
    sample_key = keys[0]
    response = s3.get_object(Bucket=BUCKET_NAME, Key=sample_key)
    body = json.loads(response["Body"].read())

    print(f"\n=== Round-trip check: downloaded {sample_key} ===")
    print(json.dumps(body, indent=2))


def main():
    s3 = get_s3_client()
    create_bucket(s3)
    upload_orders(s3)
    keys = list_and_count(s3)
    download_one(s3, keys)


if __name__ == "__main__":
    main()
