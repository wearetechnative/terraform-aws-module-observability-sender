locals {
  lambda_cw_alarm_name     = "cloudwatch_alarm_creator_${data.aws_region.current.name}"
  lambda_payload_forwarder = "payload_forwarder_${data.aws_region.current.name}"

  monitoring_account_sqs_arn = "arn:aws:sqs:${var.monitoring_account_configuration.sqs_region}:${var.monitoring_account_configuration.sqs_account}:${var.monitoring_account_configuration.sqs_name}"
  monitoring_account_sqs_url = "https://sqs.${var.monitoring_account_configuration.sqs_region}.amazonaws.com/${var.monitoring_account_configuration.sqs_account}/${var.monitoring_account_configuration.sqs_name}"

  default_eventbridge_rules = {
    "aws-cloudwatch-alarm-notification-rule" : {
      "description" : "Monitor state changes of CloudWatch alarms.",
      "state" : "ENABLED",
      "event_pattern" : jsonencode({
        "source" : ["aws.cloudwatch"],
        "detail-type" : ["CloudWatch Alarm State Change"],
        "detail": {
          "configuration": {
            "description": [ { "anything-but": "Autoscaling Alarm" } ]
          }
        }
      })
    },
    "aws-healthdashboard-notification-rule" : {
      "description" : "Monitor state AWS Health Dashboard changes.",
      "state" : "ENABLED",
      "event_pattern" : jsonencode({
        "source" : ["aws.health"],
        "detail-type" : ["AWS Health Event"],
        "detail" : {
          "service" : ["HEALTH"],
          "eventTypeCategory" : ["issue"],
          "eventTypeCode" : ["AWS_HEALTH_OPERATIONAL_ISSUE"]
        }
      })
    },
    "aws-config-notification" : {
      "description" : "Notifies of AWS Config items going out compliancy.",
      "state" : "ENABLED",
      "event_pattern" : jsonencode({
        "source" : ["aws.config"]
        "detail.eventName" : ["PutEvaluations"]
        "detail.eventSource" : ["config.amazonaws.com"]
        "detail-type" : ["AWS API Call via CloudTrail"]
        "detail.errorCode" : [{ "exists" : false }]
        "detail" : {
          "requestParameters" : {
            "evaluations" : {
              "complianceType" : ["NON_COMPLIANT"]
            }
          }
        }
      })
    },
    "aws-backup" : {
      "description" : "Notifies of AWS Backups failing.",
      "state" : "ENABLED",
      "event_pattern" : jsonencode({
        "source" : ["aws.backup"],
        "detail-type" : ["Backup Job State Change", "Copy Job State Change"],
        "detail" : {
          "state" : [{ "anything-but" : ["RUNNING", "COMPLETED", "CREATED"] }]
        }
      })
    },
    "aws-backup-cloudtrail" : {
      "description" : "Notifies of AWS Backups failing through CloudTrail events.",
      "state" : "ENABLED",
      "event_pattern" : jsonencode({
        "source" : ["aws.backup"],
        "detail-type" : ["AWS Service Event via CloudTrail"],
        "detail" : {
          "errorCode" : [{ "exists" : true }]
        }
      })
    },
    "aws-ssm-patch-manager" : {
      "description" : "Notifies when SSM patch manager fails."
      "state" : "ENABLED",
      "event_pattern" : jsonencode({
        "source" : ["aws.ssm"],
        "detail-type" : ["EC2 Command Invocation Status-change Notification", "EC2 State Manager Instance Association State Change"],
        "detail" : {
          "status" : ["Failed", "TimedOut"]
        }
      })
  } }
}
