# 02messaging.02kafka — Amazon MSK (managed Apache Kafka), brokers spread across the AZs, IAM auth over TLS.
# Used by: java _02messaging_02kafka (Spring Kafka), python _02messaging_02kafka (confluent-kafka).
# Topics are created by the app's admin code (auto-create is off on purpose).
# Per-env knobs: broker type/count, EBS size, log retention.

locals {
  component = "02messaging.02kafka"

  # RF follows broker count so small envs (2 brokers) still start; 3+ brokers get the full RF=3 / ISR=2.
  replication_factor  = min(3, var.broker_count)
  min_insync_replicas = max(1, local.replication_factor - 1)
}

resource "aws_security_group" "msk" {
  name   = "${var.prefix}-msk"
  vpc_id = var.vpc_id

  ingress {
    description     = "Kafka SASL/IAM over TLS from the app"
    from_port       = 9098
    to_port         = 9098
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }

  tags = { Component = local.component }
}

# Broker config = server.properties. These are the durability knobs that matter most.
resource "aws_msk_configuration" "x" {
  name           = "${var.prefix}-kafka-config"
  kafka_versions = ["3.6.0"]

  server_properties = <<-PROPS
    auto.create.topics.enable=false
    default.replication.factor=${local.replication_factor}
    min.insync.replicas=${local.min_insync_replicas}
    unclean.leader.election.enable=false
    num.partitions=6
    log.retention.hours=${var.log_retention_hours}
  PROPS
  # RF=3 + min.insync=2 + producer acks=all: a write survives one broker loss; with 2 down, producers get
  # NotEnoughReplicas instead of silently losing data. unclean=false: never elect an out-of-sync leader.
}

resource "aws_msk_cluster" "x" {
  cluster_name           = "${var.prefix}-kafka"
  kafka_version          = "3.6.0"
  number_of_broker_nodes = var.broker_count # must be a multiple of the subnet (AZ) count

  broker_node_group_info {
    instance_type   = var.broker_instance_type
    client_subnets  = var.subnet_ids
    security_groups = [aws_security_group.msk.id]

    storage_info {
      ebs_storage_info {
        volume_size = var.volume_size_gib # GiB per broker; size = ingress MB/s x retention x RF / brokers, plus headroom
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
    encryption_at_rest_kms_key_arn = var.kms_key_arn
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

  tags = { Component = local.component }

  lifecycle {
    precondition {
      condition     = var.broker_count % length(var.subnet_ids) == 0
      error_message = "msk_broker_count must be a multiple of the AZ (subnet) count."
    }
  }
}
