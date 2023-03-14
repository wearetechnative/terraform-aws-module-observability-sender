module "lambda_cw_alarm_creator" {
  # Pinned to a tag but needs to be updated once we add an official release tag.
  source = "git@github.com:TechNative-B-V/modules-aws.git//lambda?ref=v1.1.7"


  name              = local.lambda_cw_alarm_name
  role_arn          = module.iam_role_lambda_cw_alarm_creator.role_arn
  role_arn_provided = true
  kms_key_arn       = var.kms_key_arn

  handler     = "lambda_function.lambda_handler"
  memory_size = 128
  timeout     = 60
  runtime     = "python3.9"

  source_type               = "local"
  source_directory_location = "${path.module}/alarm_creator/"
  source_file_name          = null

  environment_variables = {
    SNS_ARN = "${var.sns_notification_receiver_topic_arn}"
  }

  sqs_dlq_arn = var.sqs_dlq_arn
}

# Cron job event rule directly tied to lambda function.
resource "aws_cloudwatch_event_rule" "refresh_alarms" {
  name        = "refresh-cloudwatch-alarms-rule"
  description = "Refresh CloudWatch alarms every 4 hours."

  event_bus_name      = "default"
  schedule_expression = "rate(4 hours)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule           = aws_cloudwatch_event_rule.refresh_alarms.id
  event_bus_name = aws_cloudwatch_event_rule.refresh_alarms.event_bus_name

  arn = module.lambda_cw_alarm_creator.lambda_function_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id_prefix = module.lambda_cw_alarm_creator.lambda_function_name
  action              = "lambda:InvokeFunction"
  function_name       = module.lambda_cw_alarm_creator.lambda_function_name
  principal           = "events.amazonaws.com"
  source_arn          = aws_cloudwatch_event_rule.refresh_alarms.arn
}

# Below rule monitor for instance changes based on an event.
resource "aws_cloudwatch_event_rule" "cloudwatch_instance_termininate_rule" {

  name        = "terminate-cw-alarms-on-instance-termination-rule"
  description = "Monitor state changes of CloudWatch alarms."
  is_enabled  = true

  event_bus_name = "default"
  event_pattern = jsonencode({
    "detail" : {
      "state" : ["terminated", "stopped"]
    },
    "detail-type" : ["EC2 Instance State-change Notification"],
    "source" : ["aws.ec2"]
  })
}

resource "aws_cloudwatch_event_target" "instance_terminate_lambda_target" {
  rule           = aws_cloudwatch_event_rule.cloudwatch_instance_termininate_rule.id
  event_bus_name = aws_cloudwatch_event_rule.cloudwatch_instance_termininate_rule.event_bus_name

  arn = module.lambda_cw_alarm_creator.lambda_function_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}

resource "aws_lambda_permission" "allow_eventbridge_instance_terminate_rule" {
  statement_id_prefix = module.lambda_cw_alarm_creator.lambda_function_name
  action              = "lambda:InvokeFunction"
  function_name       = module.lambda_cw_alarm_creator.lambda_function_name
  principal           = "events.amazonaws.com"
  source_arn          = aws_cloudwatch_event_rule.cloudwatch_instance_termininate_rule.arn
}
