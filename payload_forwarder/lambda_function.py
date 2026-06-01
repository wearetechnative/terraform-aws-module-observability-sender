import json
import boto3
import os

sqs = boto3.client("sqs", region_name="eu-central-1")
ec2 = boto3.client("ec2")

monitoring_account_sqs_url = os.environ["MONITORING_ACCOUNT_SQS_URL"]


def get_instance_name(instance_id):
    response = ec2.describe_instances(
        InstanceIds=[instance_id]
    )

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    return tag["Value"]

    return "No Reservation found"


def lambda_handler(event, context):
    print(event)
    for record in event["Records"]:

        sns_message = record["Sns"]

        try:
            alarm_event = json.loads(
                sns_message["Message"]
            )

            # Only process CloudWatch alarm events
            if (
                alarm_event.get("source") == "aws.cloudwatch"
                and alarm_event.get("detail-type")
                == "CloudWatch Alarm State Change"
            ):

                metrics = (
                    alarm_event["detail"]
                    .get("configuration", {})
                    .get("metrics", [])
                )

                if metrics:
                    metric = (
                        metrics[0]
                        .get("metricStat", {})
                        .get("metric", {})
                    )

                    if (
                        metric.get("namespace") == "AWS/EC2"
                    ):
                        instance_id = (
                            metric.get("dimensions", {})
                            .get("InstanceId")
                        )
                        if instance_id:
                            instance_name = get_instance_name(
                                instance_id
                            )

                            alarm_event[
                                "instanceName"
                            ] = instance_name
                sns_message["Message"] = json.dumps(
                    alarm_event
                )
        except Exception:
            # Forward unchanged if not a CloudWatch
            # alarm event or parsing fails
            pass

        sqs.send_message(
            QueueUrl=monitoring_account_sqs_url,
            MessageBody=json.dumps(sns_message),
        )