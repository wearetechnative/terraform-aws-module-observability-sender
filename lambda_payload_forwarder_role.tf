#--- cw-alarm-forwarder/role.tf ---

module "iam_role_lambda_payload_forwarder" {
  source = "./../../../identity_and_access_management/iam_role"

  role_name = local.lambda_payload_forwarder
  role_path = local.lambda_payload_forwarder

  customer_managed_policies = {
    "sqs_dlq" : jsondecode(data.aws_iam_policy_document.sqs_dlq.json)
    "lambda_monitoring_account_sqs_access" : jsondecode(data.aws_iam_policy_document.lambda_monitoring_sqs_access.json)
  }

  trust_relationship = {
    "lambda" : { "identifier" : "lambda.amazonaws.com", "identifier_type" : "Service", "enforce_mfa" : false, "enforce_userprincipal" : false, "external_id" : null, "prevent_account_confuseddeputy" : false },
  }

}

data "aws_iam_policy_document" "sqs_dlq" {
  statement {
    sid = "AllowDLQAccess"

    actions = ["sqs:SendMessage"]

    resources = [var.sqs_dlq_arn]
  }
}

data "aws_iam_policy_document" "lambda_monitoring_sqs_access" {
  statement {
    sid = "AllowLambdaAccessToMonitoringAccountSqs"

    effect  = "Allow"
    actions = ["sqs:*"]

    resources = [var.monitoring_account_sqs_arn]
  }
}
