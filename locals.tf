locals {
  lambda_cw_alarm_name     = "cloudwatch_alarm_creator_${data.aws_region.current.name}"
  lambda_payload_forwarder = "payload_forwarder_${data.aws_region.current.name}"
}
