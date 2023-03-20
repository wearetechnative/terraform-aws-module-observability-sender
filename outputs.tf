output "lambda_cloudwatch_alarm_creator_arn" {
  value = module.lambda_cw_alarm_creator.lambda_function_arn
}

output "lambda_cloudwatch_alarm_creator_name" {
  value = module.lambda_cw_alarm_creator.lambda_function_name
}

output "lambda_payload_forwarder_arn" {
  value = module.lambda_payload_forwarder.lambda_function_arn
}

output "lambda_payload_forwarder_name" {
  value = module.lambda_payload_forwarder.lambda_function_name
}

output "sns_topic_id" {
  value = aws_sns_topic.notification_receiver.id
}

output "sns_topic_arn" {
  value = aws_sns_topic.notification_receiver.arn
}
