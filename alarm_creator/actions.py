import boto3

from pip import main

# Create boto3 clients
CWclient = boto3.client("cloudwatch")
ec2 = boto3.resource("ec2")
rds = boto3.client("rds")
ec2client = boto3.client("ec2")

# Create alarms for Memory and disk usage received by CloudWatch Agent.
def Cwagent_alarms():

    cw_agent_response = CWclient.list_metrics(
        Namespace="CWAgent"
        , RecentlyActive='PT3H',
    )

    results = {}
    thresholds = {"alarm_threshold": ["90", "80", "75"], "priority": ["P1", "P2", "P3"]}

    running_instances = GetRunningInstances()

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
            if "InstanceId" in results["DimensionName"] and results['DimensionValue'] in running_instances:
                for priority, threshold in zip(
                    thresholds["priority"], thresholds["alarm_threshold"]
                ):
                    # Create alarm to notify when memory used is above a certain threshold.
                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-mem_used_percent > {threshold}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="mem_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(threshold),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{priority}",
                        Dimensions=[
                            {
                                "Name": "InstanceId",
                                "Value": f"{results['DimensionValue']}",
                            },
                        ],
                        Unit="Percent",
                        Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                    )

                    # Create alarm to notify when disk space in root folder is above a certain threshold.
                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/-disk_used_percent > {threshold}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(threshold),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{priority}",
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

                    # Create alarm to notify when disk space in /sys/fs/cgroup is above a certain threshold.
                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/sys/fs/cgroup-disk_used_percent > {threshold}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(threshold),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{priority}",
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

                    # Create alarm to notify when disk space in /dev is above a certain threshold.
                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/dev-disk_used_percent > {threshold}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(threshold),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{priority}",
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

                    # Create alarm to notify when disk space in /run folder is above a certain threshold.
                    CWclient.put_metric_alarm(
                        AlarmName=f"{results['DimensionValue']}-/run-disk_used_percent > {threshold}%",
                        ComparisonOperator="GreaterThanThreshold",
                        EvaluationPeriods=2,
                        MetricName="disk_used_percent",
                        Namespace="CWAgent",
                        Period=300,
                        Statistic="Average",
                        Threshold=int(threshold),
                        ActionsEnabled=True,
                        TreatMissingData="breaching",
                        AlarmDescription=f"{priority}",
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
    threshold = {"alarm_threshold": ["90", "80", "75"], "priority": ["P1", "P2", "P3"]}

    # filter the instances based on filters() above
    instances = GetRunningInstances()

    for priority, threshold in zip(threshold["priority"], threshold["alarm_threshold"]):
        for instance in instances:
            # Create alarm to notify when CPU utilization is above a certain threshold.
            CWclient.put_metric_alarm(
                AlarmName=f"{instance}-CPUUtilization > {threshold}%",
                ComparisonOperator="GreaterThanThreshold",
                EvaluationPeriods=2,
                MetricName="CPUUtilization",
                Namespace="AWS/EC2",
                Period=300,
                Statistic="Average",
                Threshold=int(threshold),
                ActionsEnabled=True,
                TreatMissingData="breaching",
                AlarmDescription=f"{priority}",
                Dimensions=[
                    {"Name": "InstanceId", "Value": f"{instance}"},
                ],
                Unit="Percent",
                Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
            )


# Create alarms for RDS databases by querying the RDS Namespace.
def RDS_Alarms():

    rds_threshold = {
        "alarm_threshold": ["2", "5", "10"],
        "priority": ["P1", "P2", "P3"],
    }

    response = CWclient.list_metrics(
        Namespace="AWS/RDS"
        , RecentlyActive='PT3H',
    )

    for metrics in response["Metrics"]:
        if metrics["MetricName"] == "FreeStorageSpace":
            for dimensions in metrics["Dimensions"]:
                if dimensions["Name"] == "DBInstanceIdentifier":
                    for priority, threshold in zip(
                        rds_threshold["priority"], rds_threshold["alarm_threshold"]
                    ):
                        threshold_in_bytes = int(threshold) * 1000000000

                        # Create alarm to notify when RDS database is running low on storage space.
                        CWclient.put_metric_alarm(
                            AlarmName=f"{dimensions['Value']}-FreeStorageSpace < {threshold} GB",
                            ComparisonOperator="LessThanOrEqualToThreshold",
                            EvaluationPeriods=2,
                            MetricName="FreeStorageSpace",
                            Namespace="AWS/RDS",
                            Period=300,
                            Statistic="Minimum",
                            Threshold=threshold_in_bytes,
                            ActionsEnabled=True,
                            TreatMissingData="breaching",
                            AlarmDescription=f"{priority}",
                            Dimensions=[
                                {
                                    "Name": "DBInstanceIdentifier",
                                    "Value": f"{dimensions['Value']}",
                                },
                            ],
                            Tags=[{"Key": "CreatedbyLambda", "Value": "True"}],
                        )

def GetRunningInstances():
    get_running_instances = ec2client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    # instantiate empty array to store instance-id's
    RunningInstances = []

    # create an array with a list of instance names
    for reservations in get_running_instances["Reservations"]:
        for instance in reservations["Instances"]:
            RunningInstances.append(instance["InstanceId"])

    return RunningInstances

def DeleteAlarms():
    get_alarm_info = CWclient.describe_alarms()
    RunningInstances = GetRunningInstances()

    # collect alarm metrics and compare alarm metric instanceId with instance id's in array. if the state reason is breaching and instance does not exist delete alarm.
    for metricalarm in get_alarm_info["MetricAlarms"]:
        instance_id = list(filter(lambda x: x["Name"] == "InstanceId", metricalarm["Dimensions"]))

        if len(instance_id) == 1:
            if instance_id[0]["Value"] not in RunningInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
