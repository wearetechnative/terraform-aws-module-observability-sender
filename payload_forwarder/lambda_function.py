import json
import boto3
import os

monitoring_account_sqs_url = os.environ["MONITORING_ACCOUNT_SQS_URL"]


def lambda_handler(event, context):

    # Region name must be set or else it defaults to a different region.
    client = boto3.client('sqs', region_name='eu-central-1')

    for record in event["Records"]:
        sns_message = record["Sns"]

        # Message must be string to be forwarded or else you will get a type error.
        sns_message_json = json.dumps(sns_message)

        # Sends message to the sqs url.
        response = client.send_message(
            QueueUrl=f"{monitoring_account_sqs_url}",
            MessageBody=sns_message_json,
        )
