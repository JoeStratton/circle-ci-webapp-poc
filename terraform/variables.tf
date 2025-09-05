
variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.aws_region))
    error_message = "AWS region must be a valid region name."
  }
}

variable "state_bucket" {
  description = "Name of existing S3 bucket for Terraform state"
  type        = string
  default     = "joes-circleci-demo-poc-state"
}

variable "project_name" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "circle-ci-webapp-poc"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "enable_fargate_spot" {
  description = "Enable Fargate Spot for cost optimization"
  type        = bool
  default     = true
}

variable "ecs_cpu" {
  description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "Memory (MB) for ECS task"
  type        = number
  default     = 512
}

variable "ecr_image_retention_count" {
  description = "Number of ECR images to retain"
  type        = number
  default     = 3
}


variable "cloudwatch_log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 1
}

variable "circleci_organization_id" {
  description = "CircleCI Organization ID (UUID) for OIDC trust policy"
  type        = string

  validation {
    condition     = can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.circleci_organization_id))
    error_message = "CircleCI Organization ID must be a valid UUID format."
  }
}

variable "circleci_project_id" {
  description = "CircleCI Project ID (UUID) for OIDC security"
  type        = string

  validation {
    condition     = can(regex("^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", var.circleci_project_id))
    error_message = "CircleCI Project ID must be a valid UUID format."
  }
}

variable "allowed_branches" {
  description = "Git branches allowed to assume the OIDC role"
  type        = list(string)
  default     = ["main", "dev"]
}

variable "database_username" {
  description = "PostgreSQL database username (passed from CircleCI context)"
  type        = string
  default     = "appuser"
}

variable "database_password" {
  description = "PostgreSQL database password (passed from CircleCI context)"
  type        = string
  sensitive   = true
  # No default - must be provided via CircleCI context
  
  validation {
    condition     = length(var.database_password) > 0
    error_message = "Database password must not be empty."
  }
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "circleci-demo"
    Environment = "dev"
    ManagedBy   = "terraform"
    Owner       = "joe"
  }
}
