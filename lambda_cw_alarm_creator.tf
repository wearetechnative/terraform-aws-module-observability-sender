module "lambda_cw_alarm_creator" {
  # Pinned to a tag but needs to be updated once we add an official release tag.
  #source = "git@github.com:TechNative-B-V/modules-aws.git//lambda?ref=v1.1.7"
  source = "git@github.com:wearetechnative/terraform-aws-lambda.git?ref=13eda5f9e8ae40e51f66a45837cd41a6b35af988"


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

  layers = var.source_directory_location != null ? [aws_lambda_layer_version.custom_actions[0].arn] : null

  environment_variables = {
    SNS_ARN             = "${aws_sns_topic.notification_receiver.arn}"
    CUSTOM_ALERT_ACTION = var.source_directory_location != null ? true : false
  }

  sqs_dlq_arn = var.sqs_dlq_arn
}

# Create Lambda layer to host custom_alarms.json

resource "aws_lambda_layer_version" "custom_actions" {
  count = var.source_directory_location != null ? 1 : 0

  layer_name  = "alarm_creator_custom_alert_actions"
  description = "Contains a customer specific custom_alarms.json used for the alarm_creator"

  filename = data.archive_file.custom_action[0].output_path

  source_code_hash = data.archive_file.custom_action[0].output_base64sha256

  compatible_runtimes = ["python3.9"]
}

# Cron job event rule directly tied to lambda function.
resource "aws_cloudwatch_event_rule" "refresh_alarms" {
  name        = "refresh-cloudwatch-alarms-rule"
  description = "Refresh CloudWatch alarms every 4 hours."

  state               = "ENABLED"
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

# Specific Eventbridge rule that triggers the lambda to remove stale cloudwatch alarms.
resource "aws_cloudwatch_event_rule" "cloudwatch_instance_termininate_rule" {

  name        = "terminate-cw-alarms-on-instance-termination-rule"
  description = "Monitor state changes of EC2 instances and if true run cw_alarm creator lambda to remove stale alarms."
  state       = "ENABLED"

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
