import boto3, json, subprocess, os, time, logging
from botocore.exceptions import ClientError

from pip import main

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# environment_variables
custom_alert_action  = os.environ['CUSTOM_ALERT_ACTION']

# Create boto3 clients
CWclient     = boto3.client('cloudwatch')
ec2          = boto3.resource('ec2')
rds          = boto3.client('rds')
ec2client    = boto3.client('ec2')
ecsclient    = boto3.client('ecs')
elasticlient = boto3.client("elasticache")

# Load json file containing the alarms, checks if it needs to use a custom alarms json or default json.
if custom_alert_action == "true":
    with open('/opt/custom_alarms.json') as alarms_file:
        alarms = json.load(alarms_file)
else:
    with open('./alarms.json') as alarms_file:
        alarms = json.load(alarms_file)

# Get running instances and store them in a list.
def GetRunningInstances():

    get_running_instances = ec2client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    # instantiate empty array to store instance-id's
    RunningInstances = []

    # Create a list of instance names 
    for reservations in get_running_instances["Reservations"]:
        for instance in reservations["Instances"]:
            for tag in instance["Tags"]:
                 # Skip instance if it has the ASG tag
                if any(tag["Key"] == "aws:autoscaling:groupName" for tag in instance["Tags"]):
                    continue
                # Otherwise add it once
                if instance["InstanceId"] not in RunningInstances:
                    RunningInstances.append(instance["InstanceId"])

    return RunningInstances

# Get running RDS database instances and store them in a list.
def GetRunningDBInstances():

    get_running_db_instances = rds.describe_db_instances()
    RunningDBInstances       = []

    for db_instance in get_running_db_instances["DBInstances"]:
        RunningDBInstances.append(db_instance["DBInstanceIdentifier"])

    return RunningDBInstances

# Get running ECS Clusters and store them in a list.
def GetRunningClusters():
    
    get_running_clusters = ecsclient.list_clusters()
    RunningClusters      = get_running_clusters["clusterArns"]
    RunningClusterNames  = []

    for clusters in RunningClusters:
        RunningClusterNames.append(clusters.split('/')[1])

    return RunningClusterNames

# Get running Cache clusters and store them in a list.
def GetRunningCacheClusters():

    get_running_cacheclusters = elasticlient.describe_cache_clusters()
    RunningCacheClusters      = []

    for cachecluster in get_running_cacheclusters['CacheClusters']:
        RunningCacheClusters.append(cachecluster['CacheClusterId'])

    return RunningCacheClusters

def get_cached_metrics(namespace, dimensions,metrics_cache):

    dim_key = tuple(sorted((d['Name'], d['Value']) for d in dimensions))
    cache_key = (namespace, dim_key)

    if cache_key not in metrics_cache:
        # Only make API call if not in cache
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
   # print(f'the response is {response}')
    host_names = []
    for metric in response['Metrics']:
        print(f'the metric is {metric}')
        for dimension in metric['Dimensions']:
            print(f'the dimension is {dimension}')
            if dimension['Name'] == 'host':
                value = dimension['Value']
                if value not in host_names:
                    host_names.append(value)
           
    return host_names

# Compare two sets of dimensions to see if they match.
def compare_dimensions(existing_dims, new_dims):

    # Compare two sets of dimensions to see if they match.
    if len(existing_dims) != len(new_dims):
        return False
        
    # Convert lists to sets of tuples for comparison
    existing_set = {(d['Name'], d['Value']) for d in existing_dims}
    new_set      = {(d['Name'], d['Value']) for d in new_dims}
    
    return existing_set == new_set

# Alarm creator
def AWS_Alarms():

    start_time = time.time()
    metrics_cache = {}
    alarm_configs = []  # Will store all alarm configurations
    existing_alarms = {}

    logger.info("Fetching existing CloudWatch alarms...")
    existing_alarms_start = time.time()

    def normalize_alarm(alarm):
        metric_name = alarm.get('MetricName')
        namespace = alarm.get('Namespace')
        dimensions = alarm.get('Dimensions', [])
        period = alarm.get('Period')
        statistic = alarm.get('Statistic') or alarm.get('ExtendedStatistic')
        metrics = alarm.get('Metrics')

        if metric_name is None and metrics:
            for m in metrics:
                ms = m.get('MetricStat')
                if not ms:
                    continue
                metric = ms.get('Metric', {})
                if metric_name is None:
                    metric_name = metric.get('MetricName')
                if namespace is None:
                    namespace = metric.get('Namespace')
                if not dimensions:
                    dimensions = metric.get('Dimensions', [])
                if period is None:
                    period = ms.get('Period')
                if statistic is None:
                    statistic = ms.get('Stat')
                break

        if metric_name is None and not metrics:
            return None

        return {
            'metric_name': metric_name,
            'namespace': namespace,
            'dimensions': dimensions or [],
            'threshold': alarm.get('Threshold'),
            'comparison_operator': alarm.get('ComparisonOperator'),
            'evaluation_periods': alarm.get('EvaluationPeriods'),
            'period': period,
            'statistic': statistic,
            'metrics': metrics,
        }

    paginator = CWclient.get_paginator('describe_alarms')
    for page in paginator.paginate(AlarmTypes=['MetricAlarm']):
        for alarm in page.get('MetricAlarms', []):
            try:
                response = CWclient.list_tags_for_resource(ResourceARN=alarm['AlarmArn'])
            except Exception as e:
                logger.warning(f"Could not list tags for alarm {alarm.get('AlarmName')}: {e}")
                continue

            has_lambda_tag = any(
                t.get('Key') == 'CreatedbyLambda' and t.get('Value') == 'True'
                for t in response.get('Tags', [])
            )
            if not has_lambda_tag:
                continue

            config = normalize_alarm(alarm)
            if config is None:
                logger.debug(f"Skipping alarm without resolvable metric: {alarm.get('AlarmName')}")
                continue

            existing_alarms[alarm['AlarmName']] = config

    logger.info(f"Found {len(existing_alarms)} existing Lambda-created alarms in {time.time() - existing_alarms_start:.2f} seconds")

    skipped_count = 0
    for service in alarms:

        dimensionlist = []

        # Fill instances variable with Running instances per service
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

        logger.info(f"Found {len(instances)} instances for service {service}")

        for alarm in alarms[service]:

            # Query the namespaces in CloudWatch Metrics
            response = get_cached_metrics(alarms[service][alarm]['Namespace'], [], metrics_cache)

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

                            dimensionlist = [instanceDimensions]

                            # Add any additional disk-related dimensions if present
                            if 'ExtraDimensions' in alarms[service][alarm]:
                                dimensionlist.extend(alarms[service][alarm]['ExtraDimensions'])

                                for dimension in dimensionlist:
                                    if dimension["Name"] == "path" and dimension["Value"] == "/":

                                        # Query the namespaces in CloudWatch Metrics and find the correct device dimension for the root volume
                                        response_2 = get_cached_metrics(
                                            alarms[service][alarm]['Namespace'], 
                                            [instanceDimensions, {'Name': 'path', 'Value': '/'}],
                                            metrics_cache
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
                            alarm_name = f"{instance}-{alarm} {alarms[service][alarm]['Description']['Operatorsymbol']} {threshold} {alarms[service][alarm]['Description']['ThresholdUnit']}"

                            # Skip if alarm exists with same config
                            if alarm_name in existing_alarms:
                                existing = existing_alarms[alarm_name]
                                
                                # Compare key configuration elements
                                if (existing['metric_name'] == alarms[service][alarm]['MetricName'] and
                                    existing['namespace'] == alarms[service][alarm]['Namespace'] and
                                    existing['threshold'] == cw_threshold and
                                    existing['comparison_operator'] == alarms[service][alarm]['ComparisonOperator']):
                                    
                                    # For a more thorough check, also compare dimensions
                                    dims_match = compare_dimensions(existing['dimensions'], dimensionlist)
                                    
                                    if dims_match:
                                        skipped_count += 1
                                        continue  # Skip this alarm, it's already created with same config

                             # Store configuration for batch processing
                            alarm_configs.append({
                                'CWclient': CWclient,
                                'alarm_name': f"{instance}-{alarm} {alarms[service][alarm]['Description']['Operatorsymbol']} {threshold} {alarms[service][alarm]['Description']['ThresholdUnit']}",
                                'comparison_operator': alarms[service][alarm]['ComparisonOperator'],
                                'evaluation_periods': alarms[service][alarm]['EvaluationPeriods'],
                                'metric_name': alarms[service][alarm]['MetricName'],
                                'namespace': alarms[service][alarm]['Namespace'],
                                'period': alarms[service][alarm]['Period'],
                                'statistic': alarms[service][alarm]['Statistic'],
                                'threshold': cw_threshold,
                                'actions_enabled': True,
                                'treat_missing_data': alarms[service][alarm]['TreatMissingData'],
                                'alarm_description': f"{priority}",
                                'dimensions': dimensionlist,
                                'tags': [{"Key": "CreatedbyLambda", "Value": "True"}]
                            })
                            
    # AFTER all loops - process ALL configs in batches
    logger.info(f"Skipped {skipped_count} existing alarms")
    logger.info(f"Collected {len(alarm_configs)} alarms to process")
                        
    # Now, process configurations in batches
    batch_size = 30  # Adjust based on testing
    total_batches = (len(alarm_configs) + batch_size - 1) // batch_size

    logger.info(f"Collected {len(alarm_configs)} alarms to process in {total_batches} batches")

    # Process in batches sequentially
    for i in range(0, len(alarm_configs), batch_size):
        batch = alarm_configs[i:i+batch_size]
        batch_num = i//batch_size + 1
        
        logger.info(f"Processing batch {batch_num}/{total_batches} with {len(batch)} alarms")
        batch_start = time.time()
        
        for config in batch:
            put_metric_alarm_with_retries(**config)
        
        logger.info(f"Completed batch {batch_num}/{total_batches} in {time.time() - batch_start:.2f} seconds")
        
        # Add a small delay between batches to avoid throttling
        if batch_num < total_batches:
            time.sleep(2)  # 2-second pause between batches
    
    logger.info(f"Alarm creation completed in {time.time() - start_time:.2f} seconds")
                        

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
