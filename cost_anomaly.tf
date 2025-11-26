resource "aws_ce_anomaly_monitor" "test" {
  name              = "AWSServiceMonitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "cost_anomaly" {
  name               = "cost-anomaly-alerts"
  frequency          = "DAILY"
  monitor_arn_list   = [aws_ce_anomaly_monitor.test.arn]
  threshold_expression {
    dimension {
      key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
      match_options = ["GREATER_THAN_OR_EQUAL"]
      values        = [tostring(var.anomaly_threshold)]
    }
  }
  subscriber {
    type    = "SNS"
    address = aws_sns_topic.notification_receiver.arn
  }
}

# resource "aws_cloudwatch_event_rule" "cost_anomaly" {
#   name        = "cost-anomaly-detection"
#   description = "Triggers when AWS Cost Anomaly Detection reports anomalies"

#   event_pattern = jsonencode({
#     "source" : ["aws.ce"],
#     "detail-type" : ["Cost Anomaly Detection Alert"],
#     "detail" : {
#         "impact" : {
#             "totalImpact" : [{ "numeric" : [">", var.anomaly_threshold] }]
#         }
#     }
#   })
# }

# resource "aws_cloudwatch_event_target" "notification_receiver" {
#   rule      = aws_cloudwatch_event_rule.cost_anomaly.name
#   target_id = "notification_receiver"
#   arn       = aws_sns_topic.notification_receiver.arn
# }
