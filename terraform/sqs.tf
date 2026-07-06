resource "aws_sqs_queue" "processing_dlq" {
  name                      = "${local.name_prefix}-processing-dlq"
  message_retention_seconds = 1209600
  tags                      = local.common_tags
}

resource "aws_sqs_queue" "processing" {
  name                       = "${local.name_prefix}-processing"
  visibility_timeout_seconds = 120
  message_retention_seconds  = 345600
  receive_wait_time_seconds  = 20

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.processing_dlq.arn
    maxReceiveCount     = 5
  })

  tags = local.common_tags
}

