locals {
  name = "${var.project_name}-${var.environment}"
}

data "aws_iam_policy_document" "github_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repository}:*"]
    }
  }
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = var.tags
}

resource "aws_iam_role" "github_deploy" {
  name               = "${local.name}-github-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_assume.json
  tags               = var.tags
}

data "aws_iam_policy_document" "github_deploy" {
  statement {
    sid = "DeployMorphixResources"
    actions = [
      "apigateway:*",
      "cloudfront:*",
      "cloudwatch:*",
      "dynamodb:*",
      "ecr:*",
      "ecs:*",
      "events:*",
      "iam:*",
      "lambda:*",
      "logs:*",
      "s3:*",
      "states:*",
      "tag:*"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "github_deploy" {
  role   = aws_iam_role.github_deploy.id
  name   = "${local.name}-github-deploy"
  policy = data.aws_iam_policy_document.github_deploy.json
}

