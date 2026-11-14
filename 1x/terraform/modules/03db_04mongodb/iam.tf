# 03db.04mongodb IAM — app-role access to DocumentDB.
#
# DocumentDB data-plane auth is in the database, not in IAM actions:
#   - SCRAM user/password: the app (or a bootstrap job) reads the managed master secret below, then creates
#     a least-privilege readWrite user for xdb. The app should not run as x_admin.
#   - IAM auth (DocumentDB 5.0+): create the user in $external mapped to the app role ARN
#     (db.getSiblingDB("$external").createUser({user: "<role arn>", mechanisms: ["MONGODB-AWS"], roles: [...]}))
#     and connect with authMechanism=MONGODB-AWS. No IAM policy action is needed for that path.
# KMS decrypt for the secret comes from the base_kms app policy.

data "aws_iam_policy_document" "app_docdb" {
  statement {
    sid       = "ReadMasterSecret"
    actions   = ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"]
    resources = [aws_docdb_cluster.docdb.master_user_secret[0].secret_arn]
  }

  statement {
    sid       = "DescribeCluster" # endpoint + instance discovery (e.g. pick the analytics replica endpoint)
    actions   = ["rds:DescribeDBClusters", "rds:DescribeDBInstances"]
    resources = [aws_docdb_cluster.docdb.arn, "arn:aws:rds:*:*:db:${var.prefix}-docdb-*"]
  }
}

resource "aws_iam_role_policy" "app_docdb" {
  name   = "docdb"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_docdb.json
}
