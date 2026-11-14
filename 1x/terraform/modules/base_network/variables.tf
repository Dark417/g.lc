variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "region" {
  description = "Region, used in VPC endpoint service names"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR; one /20 per AZ is carved from it"
  type        = string
}

variable "azs" {
  description = "AZ names to place one private subnet in each"
  type        = list(string)
}
