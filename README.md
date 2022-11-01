# Terraform AWS Observability (sender) ![](https://img.shields.io/github/workflow/status/TechNative-B-V/terraform-aws-module-name/Lint?style=plastic)

<!-- SHIELDS -->

This module implements ...

[![](we-are-technative.png)](https://www.technative.nl)

## How does it work

This Terraform module implements a serverless observability stack which can optionally create CloudWatch alarms and forwards [EventBridge events](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-events.html) to an SQS queue.

## Usage

To use this module ...

```hcl
module "observability_sender" {
  source = "git@github.com:TechNative-B-V/terraform-aws-observability-sender.git?ref=v0.0.1"

  monitoring_account_sqs_arn = " "
  monitoring_account_sqs_url = " "

  sqs_dlq_arn = " "
  kms_key_arn = " "
  sns_notification_receiver_topic_arn = " "

  eventbridge_rules = {
    "aws-backup-notification-rule" : {
      "description" : "Monitor state changes of aws backup service.",
      "enabled" : true,
      "event_pattern" : jsonencode({
        "source" : ["aws.backup"],
        "detail-type" : ["Backup Job State Change"]
      })
    }
  }
}
```

<!-- BEGIN_TF_DOCS -->
## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | > 4.3.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_iam_role_lambda_cw_alarm_creator"></a> [iam\_role\_lambda\_cw\_alarm\_creator](#module\_iam\_role\_lambda\_cw\_alarm\_creator) | git@github.com:TechNative-B-V/modules-aws.git//identity_and_access_management/iam_role | v1.1.7 |
| <a name="module_iam_role_lambda_payload_forwarder"></a> [iam\_role\_lambda\_payload\_forwarder](#module\_iam\_role\_lambda\_payload\_forwarder) | git@github.com:TechNative-B-V/modules-aws.git//identity_and_access_management/iam_role | v1.1.7 |
| <a name="module_lambda_cw_alarm_creator"></a> [lambda\_cw\_alarm\_creator](#module\_lambda\_cw\_alarm\_creator) | git@github.com:TechNative-B-V/modules-aws.git//lambda | v1.1.7 |
| <a name="module_lambda_payload_forwarder"></a> [lambda\_payload\_forwarder](#module\_lambda\_payload\_forwarder) | git@github.com:TechNative-B-V/modules-aws.git//lambda | v1.1.7 |

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.refresh_alarms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_rule.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.lambda_target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_cloudwatch_event_target.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_kms_grant.give_lambda_role_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_grant) | resource |
| [aws_lambda_permission.allow_eventbridge](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_lambda_permission.payload_forwarder](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [aws_sns_topic_policy.allow_lambda_sns_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_policy) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.cloudwatch_alarms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.eventbus](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.kms](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_cw_alarm_creator_dlq_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_ec2_read_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_monitoring_account_sqs_access_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_payload_forwarder_dlq_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.sns_topic_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/partition) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_eventbridge_rules"></a> [eventbridge\_rules](#input\_eventbridge\_rules) | EventBridge rule settings. | <pre>map(object({<br>    description : string<br>    enabled : bool<br>    event_pattern : string<br>    })<br>  )</pre> | n/a | yes |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | ARN of the KMS key. | `string` | n/a | yes |
| <a name="input_monitoring_account_sqs_arn"></a> [monitoring\_account\_sqs\_arn](#input\_monitoring\_account\_sqs\_arn) | ARN of the SQS queue in the monitoring account. | `string` | n/a | yes |
| <a name="input_monitoring_account_sqs_url"></a> [monitoring\_account\_sqs\_url](#input\_monitoring\_account\_sqs\_url) | URL of the SQS queue in the monitoring account. | `string` | n/a | yes |
| <a name="input_sns_notification_receiver_topic_arn"></a> [sns\_notification\_receiver\_topic\_arn](#input\_sns\_notification\_receiver\_topic\_arn) | ARN of the SNS topic that will receive all incoming alerts. | `string` | n/a | yes |
| <a name="input_sqs_dlq_arn"></a> [sqs\_dlq\_arn](#input\_sqs\_dlq\_arn) | ARN of the Dead Letter Queue. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_lambda_cloudwatch_alarm_creator_arn"></a> [lambda\_cloudwatch\_alarm\_creator\_arn](#output\_lambda\_cloudwatch\_alarm\_creator\_arn) | n/a |
| <a name="output_lambda_cloudwatch_alarm_creator_name"></a> [lambda\_cloudwatch\_alarm\_creator\_name](#output\_lambda\_cloudwatch\_alarm\_creator\_name) | n/a |
| <a name="output_lambda_payload_forwarder_arn"></a> [lambda\_payload\_forwarder\_arn](#output\_lambda\_payload\_forwarder\_arn) | n/a |
| <a name="output_lambda_payload_forwarder_name"></a> [lambda\_payload\_forwarder\_name](#output\_lambda\_payload\_forwarder\_name) | n/a |
<!-- END_TF_DOCS -->
