# --- EventBridge_rules/main.tf ---

resource "aws_cloudwatch_event_rule" "this" {
  for_each = { for k, v in merge(local.default_eventbridge_rules, var.eventbridge_rules) : k => v if v != null }

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

  arn = aws_sns_topic.notification_receiver.arn

  dead_letter_config {
    arn = var.sqs_dlq_arn
  }
}
