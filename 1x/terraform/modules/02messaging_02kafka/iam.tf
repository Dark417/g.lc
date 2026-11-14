# 02messaging.02kafka IAM — app-role Kafka data-plane access (cluster, topics, groups, transactional ids).

locals {
  msk_topic_arn_prefix = "arn:aws:kafka:${var.region}:${var.account_id}:topic/${aws_msk_cluster.x.cluster_name}/*"
  msk_group_arn_prefix = "arn:aws:kafka:${var.region}:${var.account_id}:group/${aws_msk_cluster.x.cluster_name}/*"
  msk_txn_arn_prefix   = "arn:aws:kafka:${var.region}:${var.account_id}:transactional-id/${aws_msk_cluster.x.cluster_name}/*"
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
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_msk.json
}
