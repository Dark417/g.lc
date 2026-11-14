variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "region" {
  description = "AWS region (endpoint service names)"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR; one private /20 per AZ is carved from it"
  type        = string
}

variable "az_count" {
  description = "Number of AZs for private subnets; 2 is enough for endpoints + OpenSearch standby"
  type        = number
}
