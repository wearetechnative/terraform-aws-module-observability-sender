import boto3
import json
import os
import logging
import traceback
import sys
import datetime
from actions import Cwagent_alarms, AWS_EC2_Alarms, RDS_Alarms, ECS_Alarms, DeleteAlarms

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("sns")
sns_arn = os.environ["SNS_ARN"]


def lambda_handler(event, context):
    print(event)

    try:
        print("{}: Cwagent_alarms()".format(datetime.datetime.now()))
        Cwagent_alarms()
        print("{}: AWS_EC2_Alarms()".format(datetime.datetime.now()))
        AWS_EC2_Alarms()
        print("{}: RDS_Alarms()".format(datetime.datetime.now()))
        RDS_Alarms()
        print("{}: ECS_Alarms()".format(datetime.datetime.now()))
        ECS_Alarms()
        print("{}: DeleteAlarms()".format(datetime.datetime.now()))
        DeleteAlarms()
        print("{}: Finished()".format(datetime.datetime.now()))
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

        raise
