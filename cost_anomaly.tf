resource "aws_ce_anomaly_monitor" "test" {
  name              = "AWSServiceMonitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "cost_anomaly" {
  name               = "cost-anomaly-alerts"
  frequency          = "IMMEDIATE"
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
