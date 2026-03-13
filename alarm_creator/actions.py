import boto3, json, os, time, logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

custom_alert_action = os.environ['CUSTOM_ALERT_ACTION']

CWclient = boto3.client('cloudwatch')
ec2 = boto3.resource('ec2')
rds = boto3.client('rds')
ec2client = boto3.client('ec2')
ecsclient = boto3.client('ecs')
elasticlient = boto3.client("elasticache")

if custom_alert_action == "true":
    with open('/opt/custom_alarms.json') as alarms_file:
        alarms = json.load(alarms_file)
else:
    with open('./alarms.json') as alarms_file:
        alarms = json.load(alarms_file)


def GetRunningInstances():

    response = ec2client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    running_instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:

            tags = instance.get("Tags", [])

            if any(tag["Key"] == "aws:autoscaling:groupName" for tag in tags):
                continue

            running_instances.append(instance["InstanceId"])

    return running_instances


def GetRunningDBInstances():

    response = rds.describe_db_instances()
    return [db["DBInstanceIdentifier"] for db in response["DBInstances"]]


def GetRunningClusters():

    response = ecsclient.list_clusters()
    return [arn.split('/')[1] for arn in response["clusterArns"]]


def GetRunningCacheClusters():

    response = elasticlient.describe_cache_clusters()
    return [c["CacheClusterId"] for c in response["CacheClusters"]]


def get_cached_metrics(namespace, dimensions, metrics_cache):

    dim_key = tuple(sorted((d['Name'], d['Value']) for d in dimensions))
    cache_key = (namespace, dim_key)

    if cache_key not in metrics_cache:
        metrics_cache[cache_key] = CWclient.list_metrics(
            Namespace=namespace,
            RecentlyActive='PT3H',
            Dimensions=dimensions
        )

    return metrics_cache[cache_key]


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


def compare_dimensions(existing_dims, new_dims):

    if len(existing_dims) != len(new_dims):
        return False

    existing_set = {(d['Name'], d['Value']) for d in existing_dims}
    new_set = {(d['Name'], d['Value']) for d in new_dims}

    return existing_set == new_set


def build_dimension_list(instanceDimensions, extra_dimensions, namespace, metrics_cache):

    dimensionlist = [instanceDimensions]

    if not extra_dimensions:
        return dimensionlist

    dimensionlist.extend(extra_dimensions)

    has_root_path = any(
        d["Name"] == "path" and d["Value"] == "/"
        for d in extra_dimensions
    )

    if not has_root_path:
        return dimensionlist

    response_root = get_cached_metrics(
        namespace,
        [instanceDimensions, {'Name': 'path', 'Value': '/'}],
        metrics_cache
    )

    found_device = None
    found_fstype = None

    for metric in response_root["Metrics"]:
        dims = {d["Name"]: d["Value"] for d in metric["Dimensions"]}

        if dims.get("path") == "/":
            found_device = dims.get("device")
            found_fstype = dims.get("fstype")
            break

    # If this is a root filesystem alarm, we need both dimensions
    # otherwise the alarm may point to a non-existent metric
    if not found_device or not found_fstype:
        logger.warning(
            "Could not resolve root filesystem dimensions for %s=%s in namespace %s",
            instanceDimensions["Name"],
            instanceDimensions["Value"],
            namespace
        )
        return None

    merged_dimensions = {
        instanceDimensions["Name"]: instanceDimensions["Value"]
    }

    for d in extra_dimensions:
        merged_dimensions[d["Name"]] = d["Value"]

    merged_dimensions["device"] = found_device
    merged_dimensions["fstype"] = found_fstype

    return [
        {"Name": name, "Value": value}
        for name, value in merged_dimensions.items()
    ]

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
        elif len(rds_instance_name) == 1:
            if rds_instance_name[0]["Value"] not in RunningRDSInstances:
                CWclient.delete_alarms(AlarmNames=[metricalarm["AlarmName"]])


def AWS_Alarms():

    start_time = time.time()
    metrics_cache = {}
    alarm_configs = []
    existing_alarms = {}

    logger.info("Fetching existing alarms...")

    paginator = CWclient.get_paginator('describe_alarms')

    for page in paginator.paginate(AlarmTypes=['MetricAlarm']):

        for alarm in page.get('MetricAlarms', []):

            try:
                response = CWclient.list_tags_for_resource(
                    ResourceARN=alarm['AlarmArn']
                )
            except Exception:
                continue

            has_lambda_tag = any(
                t['Key'] == 'CreatedbyLambda' and t['Value'] == 'True'
                for t in response.get('Tags', [])
            )

            if not has_lambda_tag:
                continue

            existing_alarms[alarm['AlarmName']] = {
                "metric_name": alarm.get('MetricName'),
                "namespace": alarm.get('Namespace'),
                "threshold": alarm.get('Threshold'),
                "comparison_operator": alarm.get('ComparisonOperator'),
                "dimensions": alarm.get('Dimensions', [])
            }

    skipped_count = 0

    for service in alarms:

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

        logger.info(f"{service}: {len(instances)} instances")

        for alarm in alarms[service]:

            response = get_cached_metrics(
                alarms[service][alarm]['Namespace'],
                [],
                metrics_cache
            )

            for metric in response["Metrics"]:

                if metric["MetricName"] != alarms[service][alarm]['MetricName']:
                    continue

                for priority, threshold in zip(
                    alarms[service][alarm]['AlarmThresholds']["priority"],
                    alarms[service][alarm]['AlarmThresholds']["alarm_threshold"]
                ):

                    if alarms[service][alarm]['Description']['ThresholdUnit'] == "GB":
                        cw_threshold = int(threshold) * 1000000000
                    elif alarms[service][alarm]['Description']['ThresholdUnit'] == "MB":
                        cw_threshold = int(threshold) * 1000000
                    else:
                        cw_threshold = int(threshold)

                    for instance in instances:

                        instanceDimensions = {
                            "Name": alarms[service][alarm]['Dimensions'],
                            "Value": instance
                        }

                        extra_dimensions = alarms[service][alarm].get('ExtraDimensions', [])

                        dimensionlist = build_dimension_list(
                            instanceDimensions,
                            extra_dimensions,
                            alarms[service][alarm]['Namespace'],
                            metrics_cache
                        )
                        if dimensionlist is None:
                            logger.info(
                                "Skipping %s for %s because no valid dimension set was found",
                                alarm,
                                instance
                            )
                            continue

                        alarm_name = f"{instance}-{alarm} {alarms[service][alarm]['Description']['Operatorsymbol']} {threshold} {alarms[service][alarm]['Description']['ThresholdUnit']}"

                        if alarm_name in existing_alarms:

                            existing = existing_alarms[alarm_name]

                            if (
                                existing['metric_name'] == alarms[service][alarm]['MetricName']
                                and existing['namespace'] == alarms[service][alarm]['Namespace']
                                and existing['threshold'] == cw_threshold
                                and existing['comparison_operator'] == alarms[service][alarm]['ComparisonOperator']
                                and compare_dimensions(existing['dimensions'], dimensionlist)
                            ):
                                skipped_count += 1
                                continue

                        alarm_configs.append({
                            "CWclient": CWclient,
                            "alarm_name": alarm_name,
                            "comparison_operator": alarms[service][alarm]['ComparisonOperator'],
                            "evaluation_periods": alarms[service][alarm]['EvaluationPeriods'],
                            "metric_name": alarms[service][alarm]['MetricName'],
                            "namespace": alarms[service][alarm]['Namespace'],
                            "period": alarms[service][alarm]['Period'],
                            "statistic": alarms[service][alarm]['Statistic'],
                            "threshold": cw_threshold,
                            "actions_enabled": True,
                            "treat_missing_data": alarms[service][alarm]['TreatMissingData'],
                            "alarm_description": priority,
                            "dimensions": dimensionlist,
                            "tags": [{"Key": "CreatedbyLambda", "Value": "True"}]
                        })

    logger.info(f"Skipped {skipped_count} alarms")
    logger.info(f"Creating {len(alarm_configs)} alarms")

    for config in alarm_configs:
        put_metric_alarm_with_retries(**config)

    logger.info(f"Completed in {time.time()-start_time:.2f}s")


def put_metric_alarm_with_retries(
        CWclient, alarm_name, comparison_operator, evaluation_periods,
        metric_name, namespace, period, statistic, threshold,
        actions_enabled, treat_missing_data, alarm_description,
        dimensions, tags, max_retries=5):

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

            return

        except ClientError as e:

            if e.response['Error']['Code'] == 'Throttling':

                retries += 1
                sleep_time = 2 ** retries
                time.sleep(sleep_time)

            else:
                raise


def lambda_handler(event, context):

    AWS_Alarms()