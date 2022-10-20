module "lambda_function" {
  source = "git@github.com:TechNative-B-V/modules-aws.git//lambda?ref=main"

  name        = "cloudwatch_alarm_creator"
  role_arn    = module.iam_role.role_arn
  kms_key_arn = var.kms_key_arn

  handler     = "lambda_function.lambda_handler"
  memory_size = 128
  timeout     = 30
  runtime     = "python3.9"

  source_type               = "local"
  source_directory_location = "${path.module}/source_alarm_creator/"
  source_file_name          = null

  environment_variables = {
    SNS_ARN = "${var.sns_notification_receiver_topic_arn}"
  }

  sqs_dlq_arn = var.sqs_dlq_arn
}

resource "aws_cloudwatch_event_rule" "refresh_alarms" {
  name        = "refresh-cloudwatch-alarms-rule"
  description = "Refresh CloudWatch alarms every 4 hours."

  event_bus_name      = "default"
  schedule_expression = "rate(4 hours)"

}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule           = aws_cloudwatch_event_rule.refresh_alarms.id
  event_bus_name = aws_cloudwatch_event_rule.refresh_alarms.event_bus_name

  arn = module.lambda_function.arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id_prefix = var.name
  action              = "lambda:InvokeFunction"
  function_name       = module.lambda_function.function_name
  principal           = "events.amazonaws.com"
  source_arn          = aws_cloudwatch_event_rule.refresh_alarms.arn
}
