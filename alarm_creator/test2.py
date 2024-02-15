import boto3, json

from pip import main

# Create boto3 clients
CWclient = boto3.client("cloudwatch")
ec2 = boto3.resource("ec2")
rds = boto3.client("rds")
ec2client = boto3.client("ec2")
ecsclient = boto3.client("ecs")

with open('./alarms.json') as alarms_file:
    alarms = json.load(alarms_file)

#print(alarms)
def AWS_Alarms():
    for service in alarms:
        if service == "EC2":
            instances = GetRunningInstances()
        elif service == "RDS":
            instances = GetRunningDBInstances()
        for alarm in alarms[service]:
        
            response = CWclient.list_metrics(
                Namespace=f"{alarms[service][alarm]['Namespace']}", RecentlyActive='PT3H',
            )
            for metrics in response["Metrics"]:
                if metrics["MetricName"] == alarms[service][alarm]['MetricName']:
                    for dimensions in metrics["Dimensions"]:
                        if dimensions["Name"] == alarms[service][alarm]['Dimensions']['Name']:
                            for priority, threshold in zip(alarms[service][alarm]['AlarmThresholds']["priority"], alarms[service][alarm]['AlarmThresholds']["alarm_threshold"]):
                                for instance in instances:
                                    CWclient.put_metric_alarm(
                                        AlarmName=f"{instance}-{alarm} > {threshold}%",
                                        ComparisonOperator=alarms[service][alarm]['ComparisonOperator'],
                                        EvaluationPeriods=alarms[service][alarm]['EvaluationPeriods'],
                                        MetricName=alarms[service][alarm]['MetricName'],
                                        Namespace=alarms[service][alarm]['Namespace'],
                                        Period=alarms[service][alarm]['Period'],
                                        Statistic=alarms[service][alarm]['Statistic'],
                                        Threshold=int(threshold),
                                        ActionsEnabled=True,
                                        TreatMissingData=alarms[service][alarm]['TreatMissingData'],
                                        AlarmDescription=f"{priority}",
                                        Dimensions=alarms[service][alarm]['Dimensions'],
                                        Unit=alarms[service][alarm]['Unit'],
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

def DeleteAlarms():
    get_alarm_info = CWclient.describe_alarms()
    RunningInstances = GetRunningInstances()
    RunningRDSInstances = GetRunningDBInstances()
    
    # collect alarm metrics and compare alarm metric instanceId with instance id's in array. if the state reason is breaching and instance does not exist delete alarm.
    for metricalarm in get_alarm_info["MetricAlarms"]:
        instance_id = list(filter(lambda x: x["Name"] == "InstanceId", metricalarm["Dimensions"]))
        rds_instance_name = list(filter(lambda x: x["Name"] == "DBInstanceIdentifier", metricalarm["Dimensions"]))
        
        if len(instance_id) == 1:
            if instance_id[0]["Value"] not in RunningInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
        if len(rds_instance_name) == 1:
            if rds_instance_name[0]["Value"] not in RunningRDSInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])
       
AWS_Alarms()       