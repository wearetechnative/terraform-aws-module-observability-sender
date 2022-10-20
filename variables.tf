# VARIABLES

variable "eventbridge_rules" {
  description = "EventBridge rule settings."
  type = map(object({
    description : string
    enabled : bool
    event_pattern : string
    })
  )
}

variable "sns_notification_receiver_topic_arn" {
  description = "ARN of the SNS topic that will receive all incoming alerts."
  type        = string
}

variable "sqs_dlq_arn" {
  description = "ARN of the Dead Letter Queue."
  type        = string
}

variable "kms_key_arn" {
  description = " ARN of the KMS key."
  type        = string
}
