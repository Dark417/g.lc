# 00.01 network — VPC, private subnets, app SG, gateway endpoints, Bedrock PrivateLink endpoint.
# In a real org the VPC usually exists already: swap these for data sources (# assumed to exist).

locals {
  vpc_cidr = "10.40.0.0/16"
}

resource "aws_vpc" "main" {
  cidr_block           = local.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true # needed for interface-endpoint private DNS names

  tags = { Name = "${local.prefix}-vpc", Component = "00.01" }
}

# One private /20 per AZ. No public subnets: data stores are never internet-facing.
resource "aws_subnet" "private" {
  count             = length(local.azs)
  vpc_id            = aws_vpc.main.id
  availability_zone = local.azs[count.index]
  cidr_block        = cidrsubnet(local.vpc_cidr, 4, count.index)

  tags = { Name = "${local.prefix}-private-${local.azs[count.index]}", Component = "00.01" }
}

# The app (ECS task / Lambda / laptop via VPN) carries this SG; data-store SGs allow it by reference.
resource "aws_security_group" "app" {
  name        = "${local.prefix}-app"
  description = "Clients of the 1A AI services"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "All outbound (AWS APIs via endpoints / NAT)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Component = "00.01" }
}

# Gateway endpoints: S3 and DynamoDB traffic stays on the AWS network and costs no NAT data charges.
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  tags              = { Component = "00.01" }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  tags              = { Component = "00.01" }
}

# Interface endpoint (PrivateLink): Bedrock runtime calls stay inside the VPC, no NAT / internet path.
# Costs per AZ-hour + per GB (order of magnitude: a few cents per hour per AZ; check the PrivateLink pricing page).
resource "aws_security_group" "endpoints" {
  name        = "${local.prefix}-endpoints"
  description = "HTTPS from the app to interface endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTPS from the app"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = { Component = "00.01" }
}

resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.region}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.endpoints.id]
  private_dns_enabled = true # the SDK's default endpoint name resolves to the private IPs
  tags                = { Component = "00.01" }
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}
