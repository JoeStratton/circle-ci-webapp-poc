# Current AWS caller identity
data "aws_caller_identity" "current" {}

# Current AWS region
data "aws_region" "current" {}

# Default VPC (cost optimization - use existing VPC)
data "aws_vpc" "default" {
  default = true
}

# Default subnets in the VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  filter {
    name   = "availability-zone"
    values = data.aws_availability_zones.available.names
  }
}

# Available availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# Default security group
data "aws_security_group" "default" {
  name   = "default"
  vpc_id = data.aws_vpc.default.id
}

# CircleCI OIDC thumbprint - static known value from https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc_verify-thumbprint.html
locals {
  circleci_thumbprint = "06b25927c42a721631c1efd9431e648fa62e1e39"
}
