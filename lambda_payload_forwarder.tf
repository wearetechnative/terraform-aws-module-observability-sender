#--- cw-alarm-forwarder/lambda.tf ---

# Sends the payload to a destination in another account by using an assume role setup.

module "lambda_payload_forwarder" {
  # Pinned to a tag but needs to be updated once we add an official release tag.
  source = "git@github.com:TechNative-B-V/modules-aws.git//lambda?ref=v1.1.7"

  name     = local.lambda_payload_forwarder
  role_arn = module.iam_role_lambda_payload_forwarder.role_arn

  role_arn_provided = true
  kms_key_arn       = var.kms_key_arn

  handler     = "lambda_function.lambda_handler"
  memory_size = 128
  timeout     = 30
  runtime     = "python3.9"

  source_type               = "local"
  source_directory_location = "${path.module}/source_payload_forwarder/"
  source_file_name          = null

  environment_variables = {
    MONITORING_ACCOUNT_SQS_URL = "${var.monitoring_account_sqs_url}"
  }

  sqs_dlq_arn = var.sqs_dlq_arn
}

resource "aws_lambda_permission" "payload_forwarder" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_payload_forwarder.lambda_function_name
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_notification_receiver_topic_arn
}

# resource "aws_lambda_function" "cw_alarm_forwarder" {
#   function_name = var.name
#   role          = module.iam_role_lambda_cw_alarm_creator.role_arn

#   architectures = ["arm64"] # optimize for speed, usage
#   runtime       = "python3.9"
#   kms_key_arn   = var.kms_key_arn


#   description = "Forwards CloudWatch Alarm payload when an Alarm is triggered."
#   filename    = "${path.module}/lambda_function.zip"

#   memory_size                    = 128
#   reserved_concurrent_executions = -1 # prevent DDos

#   package_type     = "Zip"
#   handler          = "lambda_function.lambda_handler"
#   source_code_hash = data.archive_file.lambda_source.output_base64sha256
#   publish          = true

#   environment {
#     variables = {
#       MONITORING_ACCOUNT_SQS_URL = var.monitoring_account_sqs_url
#     }
#   }

# }
