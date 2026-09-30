"""
Exercise 2: Moto vs. LocalStack - same boto3 code, two different worlds.

This script has two parts, run one after the other:

  Part A (Moto)      - a fully self-contained fake S3, running inside this
                        Python process. No Docker, no network call, nothing
                        left behind when the script ends.

  Part B (LocalStack) - talks to the real LocalStack container from
                         Exercise 1. Requires Docker Desktop + LocalStack
                         running (docker compose up -d in this folder).

The point: Part A proves your boto3 *code* is correct, fast, in a unit
test. Part B proves it against something that behaves like real AWS.
Neither replaces the other.
"""

import boto3
from moto import mock_aws

LOCALSTACK_ENDPOINT = "http://localhost:4566"
LOCALSTACK_BUCKET = "orders-raw"  # the bucket Exercise 1 already created


def part_a_moto():
    print("=== Part A: Moto (in-process, no Docker) ===")

    @mock_aws
    def run_against_fake_s3():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="test-bucket")
        s3.put_object(Bucket="test-bucket", Key="hello.txt", Body=b"hello from moto")

        body = s3.get_object(Bucket="test-bucket", Key="hello.txt")["Body"].read()
        assert body == b"hello from moto"
        print("Put + get round-trip succeeded, entirely inside this process.")
        return s3.list_buckets()["Buckets"]

    buckets = run_against_fake_s3()
    print(f"Buckets that existed *during* the mock: {[b['Name'] for b in buckets]}")

    # Prove nothing survives: a plain (non-mocked) client sees no such bucket
    real_s3 = boto3.client("s3", region_name="us-east-1")
    try:
        real_s3.list_buckets()
        print("(This line only runs if you have real AWS credentials configured.)")
    except Exception as e:
        print(f"Outside the mock, calling real AWS fails as expected: {type(e).__name__}")

    print("Moto's fake S3 no longer exists now that run_against_fake_s3() has returned.\n")


def part_b_localstack():
    print("=== Part B: LocalStack (real server, from Exercise 1) ===")

    s3 = boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )

    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    if LOCALSTACK_BUCKET not in buckets:
        raise RuntimeError(
            f"Bucket '{LOCALSTACK_BUCKET}' not found. Run exercise1_s3.py first, "
            "and make sure Docker Desktop / LocalStack are still running."
        )

    objects = s3.list_objects_v2(Bucket=LOCALSTACK_BUCKET, Prefix="orders_incoming/")
    count = objects.get("KeyCount", 0)
    print(f"Bucket '{LOCALSTACK_BUCKET}' still has {count} objects in it.")
    print("This is the key difference: LocalStack is a real, separately running")
    print("server - what Exercise 1 uploaded is still there. Moto's Part A above")
    print("left nothing behind, because it never ran a server at all.")


def main():
    part_a_moto()
    part_b_localstack()


if __name__ == "__main__":
    main()
