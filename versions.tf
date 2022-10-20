#--- root/version.tf ---

terraform {
  required_version = ">= 1.1.0, < 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "> 4.3.0"
    }
  }
}
