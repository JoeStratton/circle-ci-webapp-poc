terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket  = "joes-circleci-demo-poc-state"
    key     = "circleci-demo.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}
