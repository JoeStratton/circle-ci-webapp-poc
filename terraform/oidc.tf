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

# CircleCI OIDC thumbprint - static known value from https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
locals {
  circleci_thumbprint = "06b25927c42a721631c1efd9431e648fa62e1e39"
}