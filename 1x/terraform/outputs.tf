# outputs — names, ARNs and endpoints the Java / Python config needs, re-exported from modules.
# Output names are unchanged from the old flat stack; values now carry the env, e.g. x-dev-orders.

output "env" {
  value = var.env
}

output "prefix" {
  value = local.prefix # "<project_prefix>-<env>": every AWS name starts with this
}

# ---------------------------------------------------------------- base

output "vpc_id" {
  value = module.base_network.vpc_id
}

output "private_subnet_ids" {
  value = module.base_network.private_subnet_ids
}

output "kms_key_arn" {
  value = module.base_kms.kms_key_arn
}

output "app_role_arn" {
  value = module.base_iam.app_role_arn
}

# ---------------------------------------------------------------- 03db

output "aurora_writer_endpoint" {
  value = module._03db_01aurora.writer_endpoint
}

output "aurora_reader_endpoint" {
  value = module._03db_01aurora.reader_endpoint
}

output "aurora_master_secret_arn" {
  value = module._03db_01aurora.master_secret_arn
}

output "dynamodb_orders_table" {
  value = module._03db_02dynamodb.orders_table # x-<env>-orders
}

output "dynamodb_orders_stream_arn" {
  value = module._03db_02dynamodb.orders_stream_arn
}

output "lake_bucket" {
  value = module._03db_03s3.lake_bucket # x-<env>-lake-<account>
}

output "athena_results_bucket" {
  value = module._03db_03s3.athena_results_bucket
}

output "docdb_endpoint" {
  value = module._03db_04mongodb.endpoint # X_MONGODB_URI host: mongodb://<user>@<endpoint>:27017/?tls=true&replicaSet=rs0&retryWrites=false
}

output "docdb_reader_endpoint" {
  value = module._03db_04mongodb.reader_endpoint
}

output "docdb_master_secret_arn" {
  value = module._03db_04mongodb.master_secret_arn
}

# ---------------------------------------------------------------- 05analytics

output "athena_workgroup" {
  value = module._05analytics_01athena.workgroup
}

output "glue_database" {
  value = module._05analytics_01athena.glue_database # x_<env>_lake (Glue: underscores only)
}

output "redshift_workgroup" {
  value = module._05analytics_02redshift.workgroup
}

output "redshift_database" {
  value = module._05analytics_02redshift.database
}

output "redshift_s3_role_arn" {
  value = module._05analytics_02redshift.s3_role_arn
}

# ---------------------------------------------------------------- 02messaging

output "kinesis_stream" {
  value = module._02messaging_01kinesis.stream # x-<env>-clicks
}

output "firehose_direct" {
  value = module._02messaging_01kinesis.firehose_direct
}

output "msk_bootstrap_brokers_iam" {
  value = module._02messaging_02kafka.bootstrap_brokers_iam
}
