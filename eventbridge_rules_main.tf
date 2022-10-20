# --- EventBridge_rules/main.tf ---

resource "aws_cloudwatch_event_rule" "this" {
  for_each = { for k, v in var.eventbridge_rules : k => v }

  name        = each.key
  description = each.value.description
  is_enabled  = each.value.enabled

  event_bus_name = "default"
  event_pattern  = each.value.event_pattern

}

resource "aws_cloudwatch_event_target" "this" {
  for_each = aws_cloudwatch_event_rule.this

  rule           = each.value.id
  event_bus_name = each.value.event_bus_name

  arn = var.sns_notification_receiver_topic_arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}
