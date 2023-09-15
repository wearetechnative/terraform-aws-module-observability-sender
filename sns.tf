# Default sns topic which receives all events/payloads and forwards it to lambda notification forwarder.
resource "aws_sns_topic" "notification_receiver" {
  name              = "observability-sns-topic"
  kms_master_key_id = var.kms_key_arn
}

resource "aws_sns_topic_subscription" "lambda_eventbridge_forwarder" {

  topic_arn = aws_sns_topic.notification_receiver.arn
  protocol  = "lambda"

  endpoint               = module.lambda_payload_forwarder.lambda_function_arn
  endpoint_auto_confirms = true
  raw_message_delivery   = false
  redrive_policy         = jsonencode({ deadLetterTargetArn = var.sqs_dlq_arn })
}