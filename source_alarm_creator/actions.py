import boto3
import json
import os

from botocore.config import Config
from pip import main

# Prevent Throttling AWS API
def boto3_client(resource):
    config = Config(
        retries=dict(
            max_attempts=40
        )
    )
    client = boto3.client(
            resource,
            config=config
        )
    return client

# Create boto3 clients
CWclient = boto3_client("cloudwatch")
ec2 = boto3.resource("ec2")
rds = boto3_client("rds")
ec2client = boto3_client("ec2")

# Create alarms for Memory and disk usage received by CloudWatch Agent.
def Cwagent_alarms():

    cw_agent_response = CWclient.list_metrics(Namespace="CWAgent")

    results = {}
    priorities = {"P1": "90", "P2": "80", "P3": "75"}

    # if statement is a fix to ignore past instance metrics that were stored in the CloudWatch metrics Auto Scaling Group space.
    # This has been improved to only be in the CloudWatch Agent Space, however past instance metrics will still be avaible for 3 to 6 months.
    for metric in cw_agent_response["Metrics"]:
        found = False
        for dimension in metric["Dimensions"]:

            if "AutoScalingGroupName" == dimension["Name"]:
                found = True
            else:
                results = {
                    "DimensionValue": dimension["Value"],
                    "DimensionName": dimension["Name"],
                }

        if found == False:
            if "InstanceId" in results["DimensionName"]:
                for thresholds in priorities:
                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-mem_used_percent > {priorities[thresholds]}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="mem_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(priorities[thresholds]),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{thresholds}",
                        Dimensions=[
                            {
                                "Name": "InstanceId",
                                "Value": f"{results['DimensionValue']}",
                            },
                        ],
                        Unit="Percent",
                        Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                    )

                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/-disk_used_percent > {priorities[thresholds]}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(priorities[thresholds]),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{thresholds}",
                        Dimensions=[
                            {
                                "Name": "InstanceId",
                                "Value": f"{results['DimensionValue']}",
                            },
                            {
                                "Name": "path",
                                "Value": "/",
                            },
                            {
                                "Name": "device",
                                "Value": "nvme0n1p1",
                            },
                            {
                                "Name": "fstype",
                                "Value": "ext4",
                            },
                        ],
                        Unit="Percent",
                        Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                    )

                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/sys/fs/cgroup-disk_used_percent > {priorities[thresholds]}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(priorities[thresholds]),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{thresholds}",
                        Dimensions=[
                            {
                                "Name": "InstanceId",
                                "Value": f"{results['DimensionValue']}",
                            },
                            {
                                "Name": "path",
                                "Value": "/sys/fs/cgroup",
                            },
                            {
                                "Name": "device",
                                "Value": "tmpfs",
                            },
                            {
                                "Name": "fstype",
                                "Value": "tmpfs",
                            },
                        ],
                        Unit="Percent",
                        Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                    )

                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/dev-disk_used_percent > {priorities[thresholds]}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(priorities[thresholds]),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{thresholds}",
                        Dimensions=[
                            {
                                "Name": "InstanceId",
                                "Value": f"{results['DimensionValue']}",
                            },
                            {
                                "Name": "path",
                                "Value": "/dev",
                            },
                            {
                                "Name": "device",
                                "Value": "udev",
                            },
                            {
                                "Name": "fstype",
                                "Value": "devtmpfs",
                            },
                        ],
                        Unit="Percent",
                        Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                    )

                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/run-disk_used_percent > {priorities[thresholds]}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(priorities[thresholds]),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{thresholds}",
                        Dimensions=[
                            {
                                "Name": "InstanceId",
                                "Value": f"{results['DimensionValue']}",
                            },
                            {
                                "Name": "path",
                                "Value": "/run",
                            },
                            {
                                "Name": "device",
                                "Value": "tmpfs",
                            },
                            {
                                "Name": "fstype",
                                "Value": "tmpfs",
                            },
                        ],
                        Unit="Percent",
                        Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                    )


# Create alarms for EC2 instances based on CPU by querying the instance namespace in CloudWatch Metrics.
def AWS_EC2_Alarms():

    priorities = {"P1": "90", "P2": "80", "P3": "75"}

    # create filter for instances in running state
    filters = [{"Name": "instance-state-name", "Values": ["running"]}]

    # filter the instances based on filters() above
    instances = ec2.instances.filter(Filters=filters)

    # instantiate empty array
    RunningInstances = []

    for thresholds in priorities:
        for instance in instances:
            # for each instance, append to array and create alarm
            RunningInstances.append(instance.id)
            CWclient.put_metric_alarm(
                AlarmName=f"{instance.id}-CPUUtilization > {priorities[thresholds]}%",
                ComparisonOperator="GreaterThanThreshold",
                EvaluationPeriods=2,
                MetricName="CPUUtilization",
                Namespace="AWS/EC2",
                Period=300,
                Statistic="Average",
                Threshold=int(priorities[thresholds]),
                ActionsEnabled=True,
                TreatMissingData="breaching",
                AlarmDescription=f"{thresholds}",
                Dimensions=[
                    {"Name": "InstanceId", "Value": f"{instance.id}"},
                ],
                Unit="Percent",
                Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
            )


# Create alarms for RDS databases by querying the RDS Namespace.
def RDS_Alarms():

    rds_priorities = {"P1": "2", "P2": "5", "P3": "10"}


    response = CWclient.list_metrics(Namespace="AWS/RDS")

    for metrics in response["Metrics"]:
        if metrics["MetricName"] == "FreeStorageSpace":
            for dimensions in metrics["Dimensions"]:
                if dimensions["Name"] == "DBInstanceIdentifier":
                    for thresholds in rds_priorities:

                        threshold_in_bytes = int(rds_priorities[thresholds]) * 1000000000

                        CWclient.put_metric_alarm(
                            AlarmName=f"{dimensions['Value']}-FreeStorageSpace < {rds_priorities[thresholds]} GB",
                            ComparisonOperator="LessThanOrEqualToThreshold",
                            EvaluationPeriods=2,
                            MetricName="FreeStorageSpace",
                            Namespace="AWS/RDS",
                            Period=300,
                            Statistic="Minimum",
                            Threshold=threshold_in_bytes,
                            ActionsEnabled=True,
                            TreatMissingData="breaching",
                            AlarmDescription=f"{thresholds}",
                            Dimensions=[
                                {
                                    "Name": "DBInstanceIdentifier",
                                    "Value": f"{dimensions['Value']}",
                                },
                            ],
                            Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                        )


# Delete alarms where the instance does not exist anymore.
def DeleteAlarms():

    state_reason_breach = "Threshold Crossed: no datapoints were received for 2 periods and 2 missing datapoints were treated as [Breaching]."
    get_alarm_info = CWclient.describe_alarms()
    get_running_instances = ec2client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    # instantiate empty array
    RunningInstances = []

    # create an array with a list of instance names
    for reservations in get_running_instances["Reservations"]:
        for instances in reservations["Instances"]:
            RunningInstances.append(instances["InstanceId"])

    # collect alarm metrics and compare alarm metric instanceId with instance id's in array. if the state reason is breaching and instance does not exist delete alarm.
    for metricalarms in get_alarm_info["MetricAlarms"]:
        for dimensions in metricalarms["Dimensions"]:
            for metricalarms in get_alarm_info["MetricAlarms"]:
                for dimensions in metricalarms["Dimensions"]:
                    if (
                        dimensions["Name"] == "InstanceId"
                        and dimensions["Value"] not in RunningInstances
                        and state_reason_breach in metricalarms["StateReason"]
                    ):
                        CWclient.delete_alarms(AlarmNames=[metricalarms["AlarmName"]])
