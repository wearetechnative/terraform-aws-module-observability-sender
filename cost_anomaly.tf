resource "aws_ce_anomaly_monitor" "test" {
  name              = "AWSServiceMonitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_cloudwatch_event_rule" "cost_anomaly" {
  name        = "cost-anomaly-detection"
  description = "Triggers when AWS Cost Anomaly Detection reports anomalies"

  event_pattern = jsonencode({
    "source" : ["aws.ce"],
    "detail-type" : ["Cost Anomaly Detection Alert"],
    "detail" : {
        "impact" : {
            "totalImpact" : [{ "numeric" : [">", var.anomaly_threshold] }]
        }
    }
  })
}

resource "aws_cloudwatch_event_target" "notification_receiver" {
  rule      = aws_cloudwatch_event_rule.cost_anomaly.name
  target_id = "notification_receiver"
  arn       = aws_sns_topic.notification_receiver.arn
}
