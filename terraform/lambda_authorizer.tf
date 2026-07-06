data "archive_file" "authorizer" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_authorizer_src"
  output_path = "${path.module}/build/authorizer.zip"
}

data "aws_iam_policy_document" "authorizer_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "authorizer" {
  name               = "${local.name_prefix}-authorizer"
  assume_role_policy = data.aws_iam_policy_document.authorizer_assume_role.json
  tags               = local.common_tags
}

resource "aws_iam_role_policy_attachment" "authorizer_basic" {
  role       = aws_iam_role.authorizer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "authorizer" {
  function_name    = "${local.name_prefix}-authorizer"
  role             = aws_iam_role.authorizer.arn
  filename         = data.archive_file.authorizer.output_path
  source_code_hash = data.archive_file.authorizer.output_base64sha256
  handler          = "handler.handler"
  runtime          = "python3.12"
  timeout          = 5

  environment {
    variables = {
      ALLOWED_BEARER_PREFIX = var.allowed_bearer_prefix
    }
  }

  depends_on = [aws_cloudwatch_log_group.authorizer]
  tags       = local.common_tags
}

