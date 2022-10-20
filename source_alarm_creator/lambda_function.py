import boto3
import json
import os
import logging
import traceback
import sys
from actions import *
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("sns")
sns_arn = os.environ["SNS_ARN"]


def lambda_handler(event, context):

    # Slep added to eleviate the API calls in order to not receive an API throttling call.
    try:
        Cwagent_alarms()
        time.sleep(2.5)
        AWS_EC2_Alarms()
        time.sleep(2.5)
        RDS_Alarms()
        time.sleep(2.5)
        DeleteAlarms()
    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback
        )
        err_msg = json.dumps(
            {
                "errorType": exception_type.__name__,
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string,
            }
        )

        client.publish(
            TopicArn=f"{sns_arn}",
            Subject="Error Creating CloudWatch Alarm",
            Message=json.dumps({"default": err_msg}),
            MessageStructure="json",
        )
