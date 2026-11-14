# modules/base_network — VPC, private subnets, app SG, gateway endpoints, Bedrock PrivateLink endpoint.
# Foundation: every component that runs inside the VPC (02rag_02opensearch endpoint) takes its ids from here.
# In a real org the VPC usually exists already: swap these for data sources (# assumed to exist).

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, var.az_count)
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true # needed for interface-endpoint private DNS names

  tags = { Name = "${var.prefix}-vpc", Component = "base_network" }
}

# One private /20 per AZ. No public subnets: data stores are never internet-facing.
resource "aws_subnet" "private" {
  count             = length(local.azs)
  vpc_id            = aws_vpc.main.id
  availability_zone = local.azs[count.index]
  cidr_block        = cidrsubnet(var.vpc_cidr, 4, count.index)

  tags = { Name = "${var.prefix}-private-${local.azs[count.index]}", Component = "base_network" }
}

# The app (ECS task / Lambda / laptop via VPN) carries this SG; data-store SGs allow it by reference.
resource "aws_security_group" "app" {
  name        = "${var.prefix}-app"
  description = "Clients of the 1A AI services"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "All outbound (AWS APIs via endpoints / NAT)"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Component = "base_network" }
}

# Gateway endpoints: S3 and DynamoDB traffic stays on the AWS network and costs no NAT data charges.
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  tags              = { Component = "base_network" }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  tags              = { Component = "base_network" }
}

# Interface endpoint (PrivateLink): Bedrock runtime calls stay inside the VPC, no NAT / internet path.
# Costs per AZ-hour + per GB (order of magnitude: a few cents per hour per AZ; check the PrivateLink pricing page).
resource "aws_security_group" "endpoints" {
  name        = "${var.prefix}-endpoints"
  description = "HTTPS from the app to interface endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTPS from the app"
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = { Component = "base_network" }
}

resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.region}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.endpoints.id]
  private_dns_enabled = true # the SDK's default endpoint name resolves to the private IPs
  tags                = { Component = "base_network" }
}
