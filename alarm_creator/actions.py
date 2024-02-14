import boto3

from pip import main

# Create boto3 clients
CWclient = boto3.client("cloudwatch")
ec2 = boto3.resource("ec2")
rds = boto3.client("rds")
ec2client = boto3.client("ec2")
ecsclient = boto3.client("ecs")

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
        "alarm_threshold": ["2", "3", "4"],
        "priority": ["P1", "P2", "P3"],
        "alarm_threshold_swap": ["256", "200", "128"],
        "alarm_threshold_freemem": ["200", "250", "350"],
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
        elif metrics["MetricName"] == "SwapUsage":
            for dimensions in metrics["Dimensions"]:
                if dimensions["Name"] == "DBInstanceIdentifier":
                    for priority, threshold_swap in zip(
                        rds_threshold["priority"], 
                        rds_threshold["alarm_threshold_swap"]
                    ):
                        threshold_swap_bytes= int(threshold_swap) * 1000000

                        # Create alarm to notify when RDS database is running high on swap usage.
                        CWclient.put_metric_alarm(
                            AlarmName=f"{dimensions['Value']}-SwapUsage > {threshold_swap} MB",
                            ComparisonOperator="GreaterThanThreshold",
                            EvaluationPeriods=2,
                            MetricName="SwapUsage",
                            Namespace="AWS/RDS",
                            Period=300,
                            Statistic="Maximum",
                            Threshold=threshold_swap_bytes,
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

        elif metrics["MetricName"] == "FreeableMemory":
            for dimensions in metrics["Dimensions"]:
                if dimensions["Name"] == "DBInstanceIdentifier":
                    for priority, threshold_freemem in zip(
                        rds_threshold["priority"], 
                        rds_threshold["alarm_threshold_freemem"]
                    ):
                        threshold_mem_bytes= int(threshold_freemem) * 1000000
                        
                        # Create alarm to notify when RDS database is running low on freeable memory.
                        CWclient.put_metric_alarm(
                            AlarmName=f"{dimensions['Value']}-FreeableMemory < {threshold_freemem} MB",
                            ComparisonOperator="LessThanThreshold",
                            EvaluationPeriods=2,
                            MetricName="FreeableMemory",
                            Namespace="AWS/RDS",
                            Period=300,
                            Statistic="Maximum",
                            Threshold=threshold_mem_bytes,
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

def ECS_Alarms():

    ecs_threshold = {
        "taskcount_threshold": ["1"],
        "taskcount_priority": ["P1"],
        
    }

    response_insights = CWclient.list_metrics(
        Namespace="ECS/ContainerInsights"
        , RecentlyActive='PT3H',
    )
    response = CWclient.list_metrics(
        Namespace="AWS/ECS"
        , RecentlyActive='PT3H',
    )

    for metrics in response_insights["Metrics"]:
        if metrics["MetricName"] == "TaskCount":
            for dimensions in metrics["Dimensions"]:
                if dimensions["Name"] == "ClusterName":
                    for priority, threshold in zip(
                        ecs_threshold["taskcount_priority"], ecs_threshold["taskcount_threshold"]
                    ):
                        threshold = int(threshold)
                        # Create alarm to notify when ECS tasks number is below threshold.
                        CWclient.put_metric_alarm(
                            AlarmName=f"{dimensions['Value']}-TaskCount < {threshold}",
                            ComparisonOperator="LessThanThreshold",
                            EvaluationPeriods=2,
                            MetricName="TaskCount",
                            Namespace="ECS/ContainerInsights",
                            Period=300,
                            Statistic="Minimum",
                            Threshold=threshold,
                            ActionsEnabled=True,
                            TreatMissingData="breaching",
                            AlarmDescription=f"{priority}",
                            Dimensions=[
                                {
                                    "Name": "ClusterName",
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

def GetRunningDBInstances():
    get_running_db_instances = rds.describe_db_instances()
    RunningDBInstances = []
    for db_instance in get_running_db_instances["DBInstances"]:
        RunningDBInstances.append(db_instance["DBInstanceIdentifier"])

    return RunningDBInstances

def GetRunningClusters():
    get_running_clusters = ecsclient.list_clusters()
    RunningClusters = get_running_clusters["clusterArns"]
    RunningClusterNames = []
    for clusters in RunningClusters:
        RunningClusterNames.append(clusters.split('/')[1])

    return RunningClusterNames

def GetRunningServices():
    clusters = GetRunningClusters()
    RunningServiceNames = []
    for clustername in clusters:
        get_running_services = ecsclient.list_services(cluster = clustername)
        RunningServices = get_running_services["serviceArns"]
        for services in RunningServices:
            RunningServiceNames.append(services.split('/')[2])

    return RunningServiceNames

def DeleteAlarms():
    get_alarm_info = CWclient.describe_alarms()
    RunningInstances = GetRunningInstances()
    RunningRDSInstances = GetRunningDBInstances()
    RunningClusters = GetRunningClusters()
    RunningServices = GetRunningServices()
    # collect alarm metrics and compare alarm metric instanceId with instance id's in array. if the state reason is breaching and instance does not exist delete alarm.
    for metricalarm in get_alarm_info["MetricAlarms"]:
        instance_id = list(filter(lambda x: x["Name"] == "InstanceId", metricalarm["Dimensions"]))
        rds_instance_name = list(filter(lambda x: x["Name"] == "DBInstanceIdentifier", metricalarm["Dimensions"]))
        cluster_name = list(filter(lambda x: x["Name"] == "ClusterName", metricalarm["Dimensions"]))
        service_name = list(filter(lambda x: x["Name"] == "ServiceName", metricalarm["Dimensions"]))

        if len(instance_id) == 1:
            if instance_id[0]["Value"] not in RunningInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
        if len(rds_instance_name) == 1:
            if rds_instance_name[0]["Value"] not in RunningRDSInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
        if len(cluster_name) == 1:
            if cluster_name[0]["Value"] not in RunningClusters:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
        if len(service_name) == 1:
            if service_name[0]["Value"] not in RunningServices:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])