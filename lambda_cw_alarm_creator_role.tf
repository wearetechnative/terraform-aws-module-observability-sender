#--- cw-alarm-creator/role.tf ---

module "iam_role_lambda_cw_alarm_creator" {
  source = "git@github.com:TechNative-B-V/modules-aws.git//identity_and_access_management/iam_role?ref=v1.1.7"

  role_name = local.lambda_cw_alarm_name
  role_path = local.lambda_cw_alarm_name

  customer_managed_policies = {
    "kms" : jsondecode(data.aws_iam_policy_document.kms.json)
    "lambda_cw_alarm_creator_dlq_policy" : jsondecode(data.aws_iam_policy_document.lambda_cw_alarm_creator_dlq_policy.json)
    "cloudwatch_alarms" : jsondecode(data.aws_iam_policy_document.cloudwatch_alarms.json)
    "eventbus" : jsondecode(data.aws_iam_policy_document.eventbus.json)
    "lambda_ec2_read_access" : jsondecode(data.aws_iam_policy_document.lambda_ec2_read_access.json)
    "lambda_rds_read_access" : jsondecode(data.aws_iam_policy_document.lambda_rds_read_access.json)
  }

  trust_relationship = {
    "lambda" : { "identifier" : "lambda.amazonaws.com", "identifier_type" : "Service", "enforce_mfa" : false, "enforce_userprincipal" : false, "external_id" : null, "prevent_account_confuseddeputy" : false }
  }

}

data "aws_iam_policy_document" "kms" {
  statement {
    sid = "AllowKMSAccess"

    actions = ["kms:Decrypt",
    "kms:GenerateDataKey*"]

    resources = [var.kms_key_arn]
  }
}

data "aws_iam_policy_document" "lambda_cw_alarm_creator_dlq_policy" {
  statement {
    sid = "AllowDLQAccess"

    actions = ["sqs:SendMessage"]

    resources = [var.sqs_dlq_arn]
  }
}

data "aws_iam_policy_document" "cloudwatch_alarms" {
  statement {
    sid = "AllowCloudWatchAlarms"

    actions = ["cloudwatch:ListMetrics", "cloudwatch:DeleteAlarms", "cloudwatch:PutMetricAlarm", "cloudwatch:GetMetricStatistics", "cloudwatch:Describe*"]

    resources = ["*"]
  }
}

data "aws_iam_policy_document" "eventbus" {
  statement {
    sid = "AllowEventBridge"

    actions = ["sns:Publish"]

    resources = ["arn:aws:sns:eu-central-1:${data.aws_caller_identity.current.account_id}:*"]
  }
}

data "aws_iam_policy_document" "lambda_ec2_read_access" {
  statement {
    sid = "AllowLambdaEC2Access"

    actions = ["ec2:Describe*"]

    resources = ["*"]
  }
}

data "aws_iam_policy_document" "lambda_rds_read_access" {
  statement {
    sid = "AllowLambdaRDSAccess"

    actions = ["rds:Describe*"]

    resources = ["*"]
  }
}

# The Lambda role needs to access KMS key in order to access SNS topic.
resource "aws_kms_grant" "give_lambda_role_access" {
  name              = "lambda-role-kms-grant-access"
  key_id            = var.kms_key_arn
  grantee_principal = module.iam_role_lambda_cw_alarm_creator.role_arn
  operations        = ["Decrypt", "GenerateDataKey"]
}

# This is a work-around until Terraform allows us to attach multiple policies to an SNS role without overwriting.
resource "aws_sns_topic_policy" "allow_lambda_sns_access" {
  arn    = aws_sns_topic.notification_receiver.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

# Lambda role needs access to SNS in order to publish message if something goes wrong when creating an alarm.
data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    sid     = "AllowLambdaRoleSnsAccess"
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "AWS"
      identifiers = ["arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:role/${local.lambda_cw_alarm_name}/${local.lambda_cw_alarm_name}"]
    }

    resources = [aws_sns_topic.notification_receiver.arn]
  }

  # Give EventBridge access to publish to SNS.
  statement {
    sid     = "AllowEventBridge"
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = [aws_sns_topic.notification_receiver.arn]
  }
}
