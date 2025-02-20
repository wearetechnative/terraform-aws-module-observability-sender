#--- cw-alarm-forwarder/lambda.tf ---

# Sends the payload to a destination in another account by using an assume role setup.

module "lambda_payload_forwarder" {
  # Pinned to a tag but needs to be updated once we add an official release tag.
  source = "github.com/wearetechnative/terraform-aws-lambda.git?ref=5ba61dffd4fd93e7ec4d4883f75acab7d56847bd"

  name     = local.lambda_payload_forwarder
  role_arn = module.iam_role_lambda_payload_forwarder.role_arn

  role_arn_provided = true
  kms_key_arn       = var.kms_key_arn

  handler     = "lambda_function.lambda_handler"
  memory_size = 128
  timeout     = 30
  runtime     = "python3.9"

  source_type               = "local"
  source_directory_location = "${path.module}/payload_forwarder/"
  source_file_name          = null

  environment_variables = {
    MONITORING_ACCOUNT_SQS_URL = "${local.monitoring_account_sqs_url}"
  }

  sqs_dlq_arn = var.sqs_dlq_arn
}

resource "aws_lambda_permission" "payload_forwarder" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_payload_forwarder.lambda_function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.notification_receiver.arn
}
