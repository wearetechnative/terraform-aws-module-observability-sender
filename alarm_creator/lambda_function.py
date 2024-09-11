import boto3, json, os
import logging, traceback, sys
import datetime
from actions import AWS_Alarms, DeleteAlarms

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("sns")
sns_arn = os.environ["SNS_ARN"]



def lambda_handler(event, context):
    function_detail = context.invoked_function_arn

    try:
        print("{}: AWS_Alarms()".format(datetime.datetime.now()))
        AWS_Alarms()
        print("{}: DeleteAlarms()".format(datetime.datetime.now()))
        DeleteAlarms()
        print("{}: Finished()".format(datetime.datetime.now()))
    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(
            exception_type, exception_value, exception_traceback
        )
        # Create a JSON dump with the details to publish to the SNS topic in case of an exeception.
        err_msg = json.dumps(
            {
                "functionDetail": function_detail,
                "errorType": exception_type.__name__,
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string,
            }
        )

        # Publish the error message to the SNS topic
        client.publish(
            TopicArn=f"{sns_arn}",
            Subject=f"Error Creating CloudWatch Alarm",
            Message=json.dumps({"default": err_msg}),
            MessageStructure="json",
        )

        raise
