module "tn_monitoring_account_alertingstack" {

  source = "git@github.com:TechNative-B-V/terraform-aws-observability-sender.git?ref=v0.0.1"

  monitoring_account_sqs_arn = replace("arn:aws:sqs:eu-central-1:${data.aws_caller_identity.current.account_id}:sqs-opsgenie-lambda-queue-20220711145511259200000002", "/:${data.aws_caller_identity.current.account_id}:/", ":1234567890:")
  monitoring_account_sqs_url = replace("https://sqs.eu-central-1.amazonaws.com/${data.aws_caller_identity.current.account_id}/sqs-opsgenie-lambda-queue-20220711145511259200000002", "//${data.aws_caller_identity.current.account_id}//", "/1234567890/")

  sqs_dlq_arn                         = module.dlq.sqs_dlq_arn
  kms_key_arn                         = module.kms.kms_key_arn
  sns_notification_receiver_topic_arn = aws_sns_topic.notification_payload.arn

  eventbridge_rules = {
    "aws-backup-notification-rule" : {
      "description" : "Monitor state changes of aws backup service.",
      "enabled" : true,
      "event_pattern" : jsonencode({
        "source" : ["aws.backup"],
        "detail-type" : ["Backup Job State Change"]
      })
    },
    "aws-cloudwatch-alarm-notification-rule" : {
      "description" : "Monitor state changes of aws backup service.",
      "enabled" : true,
      "event_pattern" : jsonencode({
        "source" : ["aws.backup"],
        "detail-type" : ["Backup Job State Change"]
      })
    }
  }

}
