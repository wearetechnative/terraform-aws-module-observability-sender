#--- cw-alarm-forwarder/role.tf ---

module "iam_role_lambda_payload_forwarder" {
  source = "github.com/wearetechnative/terraform-aws-iam-role?ref=9229bbd0280807cbc49f194ff6d2741265dc108a"

  role_name = local.lambda_payload_forwarder
  role_path = local.lambda_payload_forwarder

  customer_managed_policies = {
    "lambda_payload_forwarder_dlq_policy" : jsondecode(data.aws_iam_policy_document.lambda_payload_forwarder_dlq_policy.json)
    "lambda_monitoring_account_sqs_access_policy" : jsondecode(data.aws_iam_policy_document.lambda_monitoring_account_sqs_access_policy.json)
  }

  trust_relationship = {
    "lambda" : { "identifier" : "lambda.amazonaws.com", "identifier_type" : "Service", "enforce_mfa" : false, "enforce_userprincipal" : false, "external_id" : null, "prevent_account_confuseddeputy" : false },
  }

}

data "aws_iam_policy_document" "lambda_payload_forwarder_dlq_policy" {
  statement {
    sid = "AllowDLQAccess"

    actions = ["sqs:SendMessage"]

    resources = [var.sqs_dlq_arn]
  }
}

data "aws_iam_policy_document" "lambda_monitoring_account_sqs_access_policy" {
  statement {
    sid = "AllowLambdaAccessToMonitoringAccountSqs"

    effect  = "Allow"
    actions = ["sqs:*"]

    resources = [local.monitoring_account_sqs_arn]
  }
}
