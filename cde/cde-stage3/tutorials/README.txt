Stage 3: Cloud Storage & Messaging - tutorials folder
========================================================

Follow the Lab Guide (Stage3-Cloud-Storage-Messaging-Lab-Guide.docx) for
full step-by-step instructions. This file is just an orientation map.

Folder contents:

  requirements.txt        - this stage's Python packages (boto3, moto)
  docker-compose.yml       - starts LocalStack (S3, SQS, SNS)
  .env                     - YOU create this in Setup (your LocalStack auth token).
                             It is deliberately NOT in the zip - never share it.
  scripts\
    generate_dataset.py           - creates the order-event JSON files
    exercise1_s3.py                - Exercise 1: S3 via LocalStack
    exercise2_moto_vs_localstack.py - Exercise 2: Moto vs. LocalStack
    exercise3_sqs_sns.py           - Exercise 3: SNS -> SQS fan-out
  data\
    (starts empty - orders_incoming\ is created by generate_dataset.py)

Everything runs from Command Prompt (cmd), not PowerShell. Start with the
Lab Guide's Setup section - it explains the LocalStack auth token step,
which is new and easy to miss if you've used LocalStack before.
