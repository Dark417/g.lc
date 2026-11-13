# 05.02 kafka-msk — Amazon MSK (managed Apache Kafka), 3 brokers across 3 AZs, IAM auth over TLS.
# Used by: java x05_02_kafka (Spring Kafka), python x05_02_kafka (confluent-kafka).
# Topics are created by the app's admin code (auto-create is off on purpose).

resource "aws_security_group" "msk" {
  name   = "${local.prefix}-msk"
  vpc_id = aws_vpc.main.id

  ingress {
    description     = "Kafka SASL/IAM over TLS from the app"
    from_port       = 9098
    to_port         = 9098
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = { Component = "05.02" }
}

# Broker config = server.properties. These are the durability knobs that matter most.
resource "aws_msk_configuration" "x" {
  name           = "${local.prefix}-kafka-config"
  kafka_versions = ["3.6.0"]

  server_properties = <<-PROPS
    auto.create.topics.enable=false
    default.replication.factor=3
    min.insync.replicas=2
    unclean.leader.election.enable=false
    num.partitions=6
    log.retention.hours=168
  PROPS
  # RF=3 + min.insync=2 + producer acks=all: a write survives one broker loss; with 2 down, producers get
  # NotEnoughReplicas instead of silently losing data. unclean=false: never elect an out-of-sync leader.
}

resource "aws_msk_cluster" "x" {
  cluster_name           = "${local.prefix}-kafka"
  kafka_version          = "3.6.0"
  number_of_broker_nodes = 3 # must be a multiple of the subnet (AZ) count

  broker_node_group_info {
    instance_type   = "kafka.m7g.large"
    client_subnets  = aws_subnet.private[*].id
    security_groups = [aws_security_group.msk.id]

    storage_info {
      ebs_storage_info {
        volume_size = 500 # GiB per broker; size = ingress MB/s x retention x RF / brokers, plus headroom
      }
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.x.arn
    revision = aws_msk_configuration.x.latest_revision
  }

  client_authentication {
    sasl {
      iam = true # clients sign with AWS credentials; ACLs become IAM policies
    }
    unauthenticated = false
  }

  encryption_info {
    encryption_at_rest_kms_key_arn = aws_kms_key.main.arn
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  enhanced_monitoring = "PER_TOPIC_PER_PARTITION" # needed to see per-partition lag/bytes

  open_monitoring {
    prometheus {
      jmx_exporter {
        enabled_in_broker = true
      }
      node_exporter {
        enabled_in_broker = true
      }
    }
  }

  tags = { Component = "05.02" }
}

# ---------------------------------------------------------------- app access

locals {
  msk_topic_arn_prefix = "arn:aws:kafka:${var.region}:${local.account_id}:topic/${aws_msk_cluster.x.cluster_name}/*"
  msk_group_arn_prefix = "arn:aws:kafka:${var.region}:${local.account_id}:group/${aws_msk_cluster.x.cluster_name}/*"
  msk_txn_arn_prefix   = "arn:aws:kafka:${var.region}:${local.account_id}:transactional-id/${aws_msk_cluster.x.cluster_name}/*"
}

data "aws_iam_policy_document" "app_msk" {
  statement {
    actions   = ["kafka-cluster:Connect", "kafka-cluster:DescribeCluster"]
    resources = [aws_msk_cluster.x.arn]
  }
  statement {
    actions = [
      "kafka-cluster:CreateTopic", "kafka-cluster:DescribeTopic", "kafka-cluster:AlterTopic",
      "kafka-cluster:WriteData", "kafka-cluster:ReadData",
    ]
    resources = [local.msk_topic_arn_prefix]
  }
  statement {
    actions   = ["kafka-cluster:AlterGroup", "kafka-cluster:DescribeGroup"]
    resources = [local.msk_group_arn_prefix]
  }
  statement {
    actions   = ["kafka-cluster:WriteDataIdempotently", "kafka-cluster:DescribeTransactionalId", "kafka-cluster:AlterTransactionalId"]
    resources = [aws_msk_cluster.x.arn, local.msk_txn_arn_prefix]
  }
}

resource "aws_iam_role_policy" "app_msk" {
  name   = "msk"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_msk.json
}

output "msk_bootstrap_brokers_iam" {
  value = aws_msk_cluster.x.bootstrap_brokers_sasl_iam
}
