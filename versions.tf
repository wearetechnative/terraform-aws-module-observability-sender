#--- root/version.tf ---

terraform {
  required_version = ">= 1.1.0"
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.2"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "> 4.3.0"
    }
  }
}
