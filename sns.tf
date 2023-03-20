# Default sns topic which receives all events/payloads and forwards it to lambda notification forwarder.
resource "aws_sns_topic" "notification_receiver" {
  name              = "observability-sns-topic"
  kms_master_key_id = var.kms_key_arn
}
