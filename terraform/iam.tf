data "aws_iam_policy_document" "backend_irsa_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [module.eks.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.oidc_provider, "https://", "")}:sub"
      values   = ["system:serviceaccount:docops:backend-sa"]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.oidc_provider, "https://", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "backend_irsa" {
  name               = "${local.name_prefix}-backend-irsa"
  assume_role_policy = data.aws_iam_policy_document.backend_irsa_assume_role.json
  tags               = local.common_tags
}

data "aws_iam_policy_document" "backend_irsa" {
  statement {
    sid = "S3DocumentAccess"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]
    resources = ["${aws_s3_bucket.documents.arn}/*"]
  }

  statement {
    sid       = "S3ListBucket"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.documents.arn]
  }

  statement {
    sid       = "SendProcessingMessages"
    actions   = ["sqs:SendMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.processing.arn]
  }
}

resource "aws_iam_policy" "backend_irsa" {
  name   = "${local.name_prefix}-backend-irsa"
  policy = data.aws_iam_policy_document.backend_irsa.json
  tags   = local.common_tags
}

resource "aws_iam_role_policy_attachment" "backend_irsa" {
  role       = aws_iam_role.backend_irsa.name
  policy_arn = aws_iam_policy.backend_irsa.arn
}

data "aws_iam_policy_document" "worker_irsa_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [module.eks.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.oidc_provider, "https://", "")}:sub"
      values   = ["system:serviceaccount:docops:worker-sa"]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.oidc_provider, "https://", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "worker_irsa" {
  name               = "${local.name_prefix}-worker-irsa"
  assume_role_policy = data.aws_iam_policy_document.worker_irsa_assume_role.json
  tags               = local.common_tags
}

data "aws_iam_policy_document" "worker_irsa" {
  statement {
    sid = "S3ReadDocuments"
    actions = [
      "s3:GetObject",
      "s3:GetObjectAttributes",
    ]
    resources = ["${aws_s3_bucket.documents.arn}/*"]
  }

  statement {
    sid       = "S3ListBucket"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.documents.arn]
  }

  statement {
    sid = "ConsumeProcessingMessages"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:ChangeMessageVisibility",
      "sqs:GetQueueAttributes",
    ]
    resources = [aws_sqs_queue.processing.arn]
  }
}

resource "aws_iam_policy" "worker_irsa" {
  name   = "${local.name_prefix}-worker-irsa"
  policy = data.aws_iam_policy_document.worker_irsa.json
  tags   = local.common_tags
}

resource "aws_iam_role_policy_attachment" "worker_irsa" {
  role       = aws_iam_role.worker_irsa.name
  policy_arn = aws_iam_policy.worker_irsa.arn
}

