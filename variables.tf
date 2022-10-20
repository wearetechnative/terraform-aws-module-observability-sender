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

variable "sns_topic_arn" {
  description = "SNS Topic arn"
  type        = string

}

variable "sqs_dlq_arn" {
  description = "DLQ arn"
  type        = string
}
