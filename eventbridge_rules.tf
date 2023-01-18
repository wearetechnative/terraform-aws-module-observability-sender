# --- EventBridge_rules/main.tf ---

resource "aws_cloudwatch_event_rule" "cloudwatch_alarm_rule" {

  name        = "aws-cloudwatch-alarm-notification-rule"
  description = "Monitor state changes of CloudWatch alarms."
  is_enabled  = true

  event_bus_name = "default"
  event_pattern = jsonencode({
    "source" : ["aws.cloudwatch"],
    "detail-type" : ["CloudWatch Alarm State Change"]
  })
}

resource "aws_cloudwatch_event_target" "cloudwatch_alarm_rule_target" {

  rule           = aws_cloudwatch_event_rule.cloudwatch_alarm_rule.id
  event_bus_name = "default"

  arn = var.sns_notification_receiver_topic_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_cloudwatch_event_rule" "aws_backup_rule" {

  name        = "aws-backup-notification-rule"
  description = "Monitor state changes of aws backup service."
  is_enabled  = true

  event_bus_name = "default"
  event_pattern = jsonencode({
    "source" : ["aws.backup"],
    "detail-type" : ["Backup Job State Change"]
  })
}

resource "aws_cloudwatch_event_target" "aws_backup_rule_target" {

  rule           = aws_cloudwatch_event_rule.aws_backup_rule.id
  event_bus_name = "default"

  arn = var.sns_notification_receiver_topic_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_cloudwatch_event_rule" "aws_healthdashboard_rule" {

  name        = "aws-healthdashboard-notification-rule"
  description = "Monitor state AWS Health Dashboard changes."
  is_enabled  = true

  event_bus_name = "default"
  event_pattern = jsonencode({
    "source" : ["aws.health"],
    "detail-type" : ["AWS Health Event"],
    "detail" : {
      "service" : ["HEALTH"],
      "eventTypeCategory" : ["issue"],
      "eventTypeCode" : ["AWS_HEALTH_OPERATIONAL_ISSUE"]
    }
  })
}

resource "aws_cloudwatch_event_target" "aws_healthdashboard_rule_target" {

  rule           = aws_cloudwatch_event_rule.aws_healthdashboard_rule.id
  event_bus_name = "default"

  arn = var.sns_notification_receiver_topic_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_cloudwatch_event_rule" "aws_backup_cloudtrail_rule" {

  name        = "aws-backup-cloudtrail"
  description = "Notifies of AWS Backups failing through CloudTrail events."
  is_enabled  = true

  event_bus_name = "default"
  event_pattern = jsonencode({
    "detail" : {
      "errorCode" : [{
        "exists" : true
      }]
    },
    "detail-type" : ["AWS Service Event via CloudTrail"],
    "source" : ["aws.backup"]
  })
}

resource "aws_cloudwatch_event_target" "aws_backup_cloudtrail_rule_target" {

  rule           = aws_cloudwatch_event_rule.aws_backup_cloudtrail_rule.id
  event_bus_name = "default"

  arn = var.sns_notification_receiver_topic_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_cloudwatch_event_rule" "aws_config_notification_rule" {

  name        = "aws-config-notification"
  description = "Notifies of AWS Config items going out compliancy."
  is_enabled  = true

  event_bus_name = "default"
  event_pattern = jsonencode({
    "detail" : {
      "requestParameters" : {
        "evaluations" : {
          "complianceType" : ["NON_COMPLIANT"]
        }
      }
    },
    "detail-type" : ["AWS API Call via CloudTrail"],
    "detail.errorCode" : [{
      "exists" : false
    }],
    "detail.eventName" : ["PutEvaluations"],
    "detail.eventSource" : ["config.amazonaws.com"],
    "source" : ["aws.config"]
  })
}

resource "aws_cloudwatch_event_target" "aws_config_notification_rule_target" {

  rule           = aws_cloudwatch_event_rule.aws_config_notification_rule.id
  event_bus_name = "default"

  arn = var.sns_notification_receiver_topic_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_cloudwatch_event_rule" "ssm_patch_manager_rule" {

  name        = "ssm-patch-manager-notification"
  description = "Notifies when patching via SSM patch manager fails."
  is_enabled  = true

  event_bus_name = "default"
  event_pattern = jsonencode({
    "source" : ["aws.ssm"],
    "detail-type" : ["EC2 Command Invocation Status-change Notification", "EC2 State Manager Instance Association State Change"],
    "detail" : {
      "status" : ["Failed", "TimedOut"]
    }
  })
}

resource "aws_cloudwatch_event_target" "ssm_patch_manager_rule_target" {

  rule           = aws_cloudwatch_event_rule.ssm_patch_manager_rule.id
  event_bus_name = "default"

  arn = var.sns_notification_receiver_topic_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}
