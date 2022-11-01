# Example EventBridge Rules

EventBridge rules used internally at TechNative.

```json
eventbridge_rules = {
    "aws-backup-notification-rule" : {
      "description" : "Monitor state changes of aws backup service.",
      "enabled" : true,
      "event_pattern" : jsonencode({
        "source" : ["aws.backup"],
        "detail-type" : ["Backup Job State Change"]
    }) },
    "aws-cloudwatch-alarm-notification-rule" : {
      "description" : "Monitor state changes of CloudWatch alarms.",
      "enabled" : true,
      "event_pattern" : jsonencode({
        "source" : ["aws.cloudwatch"],
        "detail-type" : ["CloudWatch Alarm State Change"]
    }) },
    "aws-healthdashboard-notification-rule" : {
      "description" : "Monitor state AWS Health Dashboard changes.",
      "enabled" : true,
      "event_pattern" : jsonencode({
        "source" : ["aws.health"],
        "detail-type" : ["AWS Health Event"],
        "detail" : {
          "service" : ["HEALTH"],
          "eventTypeCategory" : ["issue"],
          "eventTypeCode" : ["AWS_HEALTH_OPERATIONAL_ISSUE"]
        }
    }) },
    "terminate-cw-alarms-on-instance-termination-rule" : {
      "description" : "Monitors for instance terminate state in order to clean up alarms..",
      "enabled" : true,
      "event_pattern" : jsonencode({
        "source" : ["aws.ec2"],
        "detail-type" : ["EC2 Instance State-change Notification"],
        "detail" : {
          "state" : ["terminated"]
    } }) }
  }
```
