# VARIABLES

variable "eventbridge_rules" {
  description = "EventBridge rule settings."
  type = map(object({
    description : string
    enabled : string
    event_pattern : string
    })
  )
  default = {}
}

variable "sqs_dlq_arn" {
  description = "ARN of the Dead Letter Queue."
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key."
  type        = string
}

variable "monitoring_account_configuration" {
  description = "Configuration settings of the monitoring account."
  type = object({
    sqs_name    = string
    sqs_region  = string
    sqs_account = number
  })
}
