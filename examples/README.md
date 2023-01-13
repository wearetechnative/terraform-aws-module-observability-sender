# Examples

## module example

```terraform
module "tn_monitoring_account_alertingstack" {

  source = "git@github.com:TechNative-B-V/terraform-aws-observability-sender.git?ref=v0.0.1"

  monitoring_account_sqs_arn = replace("arn:aws:sqs:eu-central-1:${data.aws_caller_identity.current.account_id}:sqs-opsgenie-lambda-queue-20220711145511259200000002", "/:${data.aws_caller_identity.current.account_id}:/", ":1234567890:")
  monitoring_account_sqs_url = replace("https://sqs.eu-central-1.amazonaws.com/${data.aws_caller_identity.current.account_id}/sqs-opsgenie-lambda-queue-20220711145511259200000002", "//${data.aws_caller_identity.current.account_id}//", "/1234567890/")

  sqs_dlq_arn                         = module.dlq.sqs_dlq_arn
  kms_key_arn                         = module.kms.kms_key_arn
  sns_notification_receiver_topic_arn = aws_sns_topic.notification_payload.arn
}
```

## Testing an event flow
A fast way to quickly test an event is to create a message in the SNS topic with an example payload.

It is important that the json payload has the below structure or else you will receive an error. Standard events in the AWS documentation follows the below pattern.

Example payload
```json
{
    "version": "0",
    "id": "b9baa007-2f33-0eb1-5760-0d02a572d81f",
    "detail-type": "ECS Service Action",
    "source": "aws.ecs",
    "account": "111122223333",
    "time": "2019-11-19T19:37:00Z",
    "region": "us-west-2",
    "resources": [
        "arn:aws:ecs:us-west-2:111122223333:service/default/servicetest"
    ],
    "detail": {
        "eventType": "INFO",
        "eventName": "CAPACITY_PROVIDER_STEADY_STATE",
        "clusterArn": "arn:aws:ecs:us-west-2:111122223333:cluster/default",
        "capacityProviderArns": [
            "arn:aws:ecs:us-west-2:111122223333:capacity-provider/ASG-tutorial-capacity-provider"
        ],
        "createdAt": "2019-11-19T19:37:00.807Z"
    }
}
```
