"""
Exercise 3: Announce orders with SNS, pick them up with SQS.

Run from tutorials\\data, same folder as Exercises 1-2.

What this script does, in order:
  1. Creates an SNS topic called "order-events"
  2. Creates an SQS queue called "order-queue"
  3. Subscribes the queue to the topic, with raw message delivery
     (so the queue gets your plain JSON, not SNS's wrapper envelope)
  4. Publishes an "order placed" notification for the first 5 orders
  5. Reads the messages back off the queue and deletes each after reading
     (deleting is what marks a message as "handled" in SQS)
"""

import json
import time
from pathlib import Path

import boto3

ENDPOINT_URL = "http://localhost:4566"
TOPIC_NAME = "order-events"
QUEUE_NAME = "order-queue"
LOCAL_FOLDER = Path("orders_incoming")
NUM_TO_PUBLISH = 5


def get_clients():
    session_kwargs = dict(
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )
    sns = boto3.client("sns", **session_kwargs)
    sqs = boto3.client("sqs", **session_kwargs)
    return sns, sqs


def create_topic(sns):
    response = sns.create_topic(Name=TOPIC_NAME)  # idempotent - safe to re-run
    topic_arn = response["TopicArn"]
    print(f"Topic ready: {topic_arn}")
    return topic_arn


def create_queue(sqs):
    response = sqs.create_queue(QueueName=QUEUE_NAME)  # idempotent - safe to re-run
    queue_url = response["QueueUrl"]
    queue_arn = sqs.get_queue_attributes(
        QueueUrl=queue_url, AttributeNames=["QueueArn"]
    )["Attributes"]["QueueArn"]
    print(f"Queue ready: {queue_url}")
    return queue_url, queue_arn


def subscribe_queue_to_topic(sns, topic_arn, queue_arn):
    subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn)["Subscriptions"]
    already_subscribed = any(s["Endpoint"] == queue_arn for s in subs)
    if already_subscribed:
        print("Queue is already subscribed to the topic - skipping.")
        return

    sns.subscribe(
        TopicArn=topic_arn,
        Protocol="sqs",
        Endpoint=queue_arn,
        Attributes={"RawMessageDelivery": "true"},
    )
    print("Subscribed the queue to the topic (raw message delivery on).")


def publish_order_events(sns, topic_arn):
    files = sorted(LOCAL_FOLDER.glob("order_*.json"))[:NUM_TO_PUBLISH]
    if not files:
        raise FileNotFoundError(
            f"No order files found in {LOCAL_FOLDER}\\ - run generate_dataset.py first."
        )

    for file_path in files:
        with open(file_path) as f:
            order = json.load(f)
        sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(order),
            Subject="order-placed",
        )

    print(f"Published {len(files)} order-placed notifications to the topic.")


def read_and_delete_messages(sqs, queue_url):
    print("\n=== Reading messages off the queue ===")
    # SNS->SQS delivery isn't instant - a short wait avoids an empty first read
    time.sleep(2)

    received_count = 0
    empty_reads = 0
    while empty_reads < 2:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2,  # long polling - waits briefly instead of failing fast
        )
        messages = response.get("Messages", [])
        if not messages:
            empty_reads += 1
            continue

        for msg in messages:
            order = json.loads(msg["Body"])
            print(f"  Received: {order['order_id']} - {order['product']} "
                  f"({order['status']})")
            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
            received_count += 1

    print(f"\nTotal messages received and deleted: {received_count}")
    return received_count


def main():
    sns, sqs = get_clients()
    topic_arn = create_topic(sns)
    queue_url, queue_arn = create_queue(sqs)
    subscribe_queue_to_topic(sns, topic_arn, queue_arn)
    publish_order_events(sns, topic_arn)
    read_and_delete_messages(sqs, queue_url)


if __name__ == "__main__":
    main()
