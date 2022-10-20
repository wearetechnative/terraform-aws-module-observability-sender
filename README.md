> START INSTRUCTION FOR TECHNATIVE ENGINEERS

# terraform-aws-module-template

Template for creating a new TerraForm AWS Module. For TechNative Engineers.

## Instructions

### Your Module Name

Think hard and come up with the shortest descriptive name for your module.
Look at competition in the [terraform
registry](https://registry.terraform.io/).

Your module name should be max. three words seperated by dashes. E.g.

- html-form-action
- new-account-notifier
- budget-alarms
- fix-missing-tags

### Setup Github Project

1. Click the template button on the top right...
2. Name github project `terraform-aws-[your-module-name]`
3. Make project private untill ready for publication
2. Install `pre-commit`

### Develop your module

1. Develop your module
2. Try to use the [best practices for TerraForm
   development](https://www.terraform-best-practices.com/) and [TerraForm AWS
   Development](https://github.com/ozbillwang/terraform-best-practices).

## Finish project documentation

1. Set well written title
2. Add one or more shields
3. Start readme with a short and complete as possible module description. This
   is the part where you sell your module.
4. Complete README with well written documentation. Try to think as a someone
   with three months of Terraform experience.
5. Check if pre-commit correctly generates the standard Terraform documentation.

## Publish module

If your module is in a state that it could be useful for others and ready for
publication, you can publish a first version.

1. Create a [Github
   Release](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)
2. Publish in the TerraForm Registry under the Technative Namespace (the GitHub
   Repo must be in the TechNative Organization)

---

> END INSTRUCTION FOR TECHNATIVE ENGINEERS


# Terraform AWS [Module Name] ![](https://img.shields.io/github/workflow/status/TechNative-B-V/terraform-aws-module-name/Lint?style=plastic)

<!-- SHIELDS -->

This module implements ...

[![](we-are-technative.png)](https://www.technative.nl)

## How does it work

...

## Usage

To use this module ...

```json
{
  "some_conf": "might need explanation"
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
| [aws_iam_policy_document.lambda_monitoring_sqs_access_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_payload_forwarder_dlq_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.sns_topic_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_partition.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/partition) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_eventbridge_rules"></a> [eventbridge\_rules](#input\_eventbridge\_rules) | EventBridge rule settings. | <pre>map(object({<br>    description : string<br>    enabled : bool<br>    event_pattern : string<br>    })<br>  )</pre> | n/a | yes |
| <a name="input_kms_key_arn"></a> [kms\_key\_arn](#input\_kms\_key\_arn) | ARN of the KMS key. | `string` | n/a | yes |
| <a name="input_sns_notification_receiver_topic_arn"></a> [sns\_notification\_receiver\_topic\_arn](#input\_sns\_notification\_receiver\_topic\_arn) | ARN of the SNS topic that will receive all incoming alerts. | `string` | n/a | yes |
| <a name="input_sqs_dlq_arn"></a> [sqs\_dlq\_arn](#input\_sqs\_dlq\_arn) | ARN of the Dead Letter Queue. | `string` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
