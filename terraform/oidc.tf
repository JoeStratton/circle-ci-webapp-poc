# CircleCI OIDC Provider and IAM Role
# Environment-level security setup for CI/CD authentication

# OIDC Identity Provider for CircleCI
resource "aws_iam_openid_connect_provider" "circleci" {
  url = "https://oidc.circleci.com/org/${var.circleci_organization_id}"

  client_id_list = [
    var.circleci_organization_id
  ]

  thumbprint_list = [
    local.circleci_thumbprint
  ]

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-circleci-oidc"
  })
}

# IAM Role for CircleCI OIDC Authentication
resource "aws_iam_role" "circleci_oidc_role" {
  name = "${var.project_name}-circleci-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.circleci.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "oidc.circleci.com/org/${var.circleci_organization_id}:aud" = var.circleci_organization_id
            "oidc.circleci.com/org/${var.circleci_organization_id}:ref" = [
              for branch in var.allowed_branches : "refs/heads/${branch}"
            ]
          }
          StringLike = {
            "oidc.circleci.com/org/${var.circleci_organization_id}:sub" = "org/${var.circleci_organization_id}/project/${var.circleci_project_id}/user/*"
          }
        }
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-circleci-role"
  })
}

# IAM Policy for CircleCI - ECS and ECR permissions
resource "aws_iam_policy" "circleci_ecs_ecr_policy" {
  name        = "${var.project_name}-circleci-ecs-ecr-policy"
  description = "Policy for CircleCI to manage ECS and ECR resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          # ECR permissions for image management
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          # ECS permissions for service management
          "ecs:DescribeClusters",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition",
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeTasks",
          "ecs:ListTasks"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          # IAM permissions for task execution
          "iam:PassRole"
        ]
        Resource = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.project_name}-ecs-*"
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-circleci-ecs-ecr-policy"
  })
}


# IAM Policy for CircleCI - CloudWatch Logs permissions
resource "aws_iam_policy" "circleci_logs_policy" {
  name        = "${var.project_name}-circleci-logs-policy"
  description = "Policy for CircleCI to access CloudWatch logs"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.project_name}-*"
      }
    ]
  })

  tags = merge(var.common_tags, {
    Name = "${var.project_name}-circleci-logs-policy"
  })
}

# Attach policies to the CircleCI role
resource "aws_iam_role_policy_attachment" "circleci_ecs_ecr_attachment" {
  role       = aws_iam_role.circleci_oidc_role.name
  policy_arn = aws_iam_policy.circleci_ecs_ecr_policy.arn
}


resource "aws_iam_role_policy_attachment" "circleci_logs_attachment" {
  role       = aws_iam_role.circleci_oidc_role.name
  policy_arn = aws_iam_policy.circleci_logs_policy.arn
}
