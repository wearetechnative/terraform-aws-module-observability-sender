import boto3, json, subprocess, os, time
from botocore.exceptions import ClientError

from pip import main

# environment_variables
custom_alert_action  = os.environ['CUSTOM_ALERT_ACTION']

# Create boto3 clients
CWclient = boto3.client("cloudwatch")
ec2 = boto3.resource("ec2")
rds = boto3.client("rds")
ec2client = boto3.client("ec2")
ecsclient = boto3.client("ecs")
elasticlient = boto3.client("elasticache")

# Create Lambda layer create if statement to choose which one depending on which variable is enabled.


# Load json file containing the alarms, checks if it needs to use a custom alarms json or default json.
if custom_alert_action == "true":
    with open('/opt/custom_alarms.json') as alarms_file:
        alarms = json.load(alarms_file)
else:
    with open('./alarms.json') as alarms_file:
        alarms = json.load(alarms_file)

# Alarm creator
def AWS_Alarms():
    for service in alarms:

        dimensionlist = []
        # instances = None
        #Fill instances variable with Running instances per service
        if service == "EC2":
            instances = GetRunningInstances()
        elif service == "RDS":
            instances = GetRunningDBInstances()
        elif service == "CWAgent":
            instances = GetRunningInstances()
        elif service == "ECS":
            instances = GetRunningClusters()
        elif service == "ElastiCache":
            instances = GetRunningCacheClusters()
        elif service == "Hosts":
            instances = GetHostnames()

        for alarm in alarms[service]:
            # Query the namespaces in CloudWatch Metrics
            response = CWclient.list_metrics(Namespace=f"{alarms[service][alarm]['Namespace']}", RecentlyActive='PT3H')

            for metrics in response["Metrics"]:

                # Check if any of the found metric names are equal to metric names in alarms file
                if metrics["MetricName"] == alarms[service][alarm]['MetricName']:
                    for priority, threshold in zip(alarms[service][alarm]['AlarmThresholds']["priority"], alarms[service][alarm]['AlarmThresholds']["alarm_threshold"]):
                        # Convert thresholds to bytes if needed
                        if alarms[service][alarm]['Description']['ThresholdUnit'] == "GB":
                            cw_threshold = int(threshold) * 1000000000
                        elif alarms[service][alarm]['Description']['ThresholdUnit'] == "MB":
                            cw_threshold = int(threshold) * 1000000
                        else:
                            cw_threshold = int(threshold)

                        # Handling dimensions
                        for instance in instances:

                            instanceDimensions = {
                                "Name": f"{alarms[service][alarm]['Dimensions']}",
                                "Value": instance
                            }

                            #Add any additional disk-related dimensions if present
                            if 'ExtraDimensions' in alarms[service][alarm]:
                                dimensionlist.extend(alarms[service][alarm]['ExtraDimensions'])

                                for dimension in dimensionlist:
                                    if dimension["Name"] == "path" and dimension["Value"] == "/":
                                        # Query the namespaces in CloudWatch Metrics
                                        # Find the correct device dimension for the root volume
                                        response_2 = CWclient.list_metrics(Namespace=f"{alarms[service][alarm]['Namespace']}", RecentlyActive='PT3H',
                                            Dimensions=[instanceDimensions, {'Name': 'path', 'Value': '/'}]
                                        )

                                        for metrics in response_2["Metrics"]:
                                            for dimension in metrics["Dimensions"]:
                                                if dimension['Name'] == "device":

                                                    dimensionlist = [
                                                        instanceDimensions,
                                                        {
                                                            "Name": "device",
                                                            "Value": f"{dimension['Value']}"
                                                        }
                                                    ]
                                                    dimensionlist.extend(alarms[service][alarm]['ExtraDimensions'])
                                    else:
                                        continue
                            else:
                                #Clean up dimensionlist if not extra dimensions are present and only add the instance dimension
                                dimensionlist = []
                                dimensionlist = [instanceDimensions]


                            # Create the alarms using the retry function
                            put_metric_alarm_with_retries(
                                CWclient=CWclient,
                                alarm_name=f"{instance}-{alarm} {alarms[service][alarm]['Description']['Operatorsymbol']} {threshold} {alarms[service][alarm]['Description']['ThresholdUnit']}",
                                comparison_operator=alarms[service][alarm]['ComparisonOperator'],
                                evaluation_periods=alarms[service][alarm]['EvaluationPeriods'],
                                metric_name=alarms[service][alarm]['MetricName'],
                                namespace=alarms[service][alarm]['Namespace'],
                                period=alarms[service][alarm]['Period'],
                                statistic=alarms[service][alarm]['Statistic'],
                                threshold=cw_threshold,
                                actions_enabled=True,
                                treat_missing_data=alarms[service][alarm]['TreatMissingData'],
                                alarm_description=f"{priority}",
                                dimensions=dimensionlist,
                                tags=[{"Key": "CreatedbyLambda", "Value": "True"}]
                            )

# A helper function to handle retries with exponential backoff to prevent throttling.
def put_metric_alarm_with_retries(CWclient, alarm_name, comparison_operator, evaluation_periods, metric_name, namespace, period, statistic, threshold, actions_enabled, treat_missing_data, alarm_description, dimensions, tags, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            CWclient.put_metric_alarm(
                AlarmName=alarm_name,
                ComparisonOperator=comparison_operator,
                EvaluationPeriods=evaluation_periods,
                MetricName=metric_name,
                Namespace=namespace,
                Period=period,
                Statistic=statistic,
                Threshold=threshold,
                ActionsEnabled=actions_enabled,
                TreatMissingData=treat_missing_data,
                AlarmDescription=alarm_description,
                Dimensions=dimensions,
                Tags=tags
            )
            break
        except ClientError as e:
            if e.response['Error']['Code'] == 'Throttling':
                retries += 1
                sleep_time = 2 ** retries
                time.sleep(sleep_time)
            else:
                raise

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

def GetRunningCacheClusters():
    get_running_cacheclusters = elasticlient.describe_cache_clusters()
    RunningCacheClusters = []
    for cachecluster in get_running_cacheclusters["CacheClusters"]:
        RunningCacheClusters.append(cachecluster['CacheClusterId'])

    return RunningCacheClusters

def GetHostnames():
    response = CWclient.list_metrics(
        Namespace='Hosts',
        RecentlyActive='PT3H'
    )
    host_names = []
    for metric in response['Metrics']:
        for dimension in metric['Dimensions']:
            if dimension['Name'] == 'host':
                value = dimension['Value']
                if value not in host_names:
                    host_names.append(value)
           
    return host_names

def DeleteAlarms():
    get_alarm_info = CWclient.describe_alarms()
    RunningInstances = GetRunningInstances()
    RunningRDSInstances = GetRunningDBInstances()
    RunningClusters = GetRunningClusters()

    # collect alarm metrics and compare alarm metric instanceId with instance id's in array. if the state reason is breaching and instance does not exist delete alarm.
    for metricalarm in get_alarm_info["MetricAlarms"]:
        instance_id = list(filter(lambda x: x["Name"] == "InstanceId", metricalarm["Dimensions"]))
        rds_instance_name = list(filter(lambda x: x["Name"] == "DBInstanceIdentifier", metricalarm["Dimensions"]))
        cluster_name = list(filter(lambda x: x["Name"] == "ClusterName", metricalarm["Dimensions"]))

        if len(instance_id) == 1:
            if instance_id[0]["Value"] not in RunningInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
        elif len(rds_instance_name) == 1:
            if rds_instance_name[0]["Value"] not in RunningRDSInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
        elif len(cluster_name) == 1:
            if cluster_name[0]["Value"] not in RunningClusters:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
