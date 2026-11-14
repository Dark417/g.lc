# main — one module block per component. Foundation (base_*) outputs are wired into every component;
# component-to-component links (lake bucket -> Athena / Redshift / Firehose) also go through here.
#
#   base_network --vpc, subnets, app SG--------------> aurora, docdb, redshift, kafka
#   base_iam     --app role----------> base_kms + every component iam.tf
#   base_kms     --CMK----------------------------------> every data store
#   03db_03s3        --lake + results buckets---------------> athena, redshift, kinesis

# ---------------------------------------------------------------- base

module "base_network" {
  source = "./modules/base_network"

  prefix   = local.prefix
  region   = var.region
  vpc_cidr = var.vpc_cidr
  azs      = local.azs
}

module "base_iam" {
  source = "./modules/base_iam"

  prefix = local.prefix
}

module "base_kms" {
  source = "./modules/base_kms"

  prefix               = local.prefix
  deletion_window_days = var.kms_deletion_window_days
  app_role_id          = module.base_iam.app_role_id
}

# ---------------------------------------------------------------- 03db

module "_03db_01aurora" {
  source = "./modules/03db_01aurora"

  prefix                = local.prefix
  region                = var.region
  account_id            = local.account_id
  vpc_id                = module.base_network.vpc_id
  subnet_ids            = module.base_network.private_subnet_ids
  app_security_group_id = module.base_network.app_security_group_id
  kms_key_arn           = module.base_kms.kms_key_arn
  kms_key_id            = module.base_kms.kms_key_id
  app_role_id           = module.base_iam.app_role_id

  min_acu               = var.aurora_min_acu
  max_acu               = var.aurora_max_acu
  instance_count        = var.aurora_instance_count
  deletion_protection   = var.aurora_deletion_protection
  backup_retention_days = var.aurora_backup_retention_days
  log_retention_days    = var.log_retention_days
}

module "_03db_02dynamodb" {
  source = "./modules/03db_02dynamodb"

  prefix      = local.prefix
  kms_key_arn = module.base_kms.kms_key_arn
  app_role_id = module.base_iam.app_role_id

  billing_mode        = var.dynamodb_billing_mode
  read_capacity       = var.dynamodb_read_capacity
  write_capacity      = var.dynamodb_write_capacity
  deletion_protection = var.dynamodb_deletion_protection
}

module "_03db_03s3" {
  source = "./modules/03db_03s3"

  prefix      = local.prefix
  account_id  = local.account_id
  kms_key_arn = module.base_kms.kms_key_arn
  app_role_id = module.base_iam.app_role_id

  raw_ia_days                    = var.s3_raw_ia_days
  raw_glacier_days               = var.s3_raw_glacier_days
  noncurrent_expiration_days     = var.s3_noncurrent_expiration_days
  athena_results_expiration_days = var.s3_athena_results_expiration_days
}

module "_03db_04mongodb" {
  source = "./modules/03db_04mongodb"

  prefix                = local.prefix
  vpc_id                = module.base_network.vpc_id
  subnet_ids            = module.base_network.private_subnet_ids
  app_security_group_id = module.base_network.app_security_group_id
  kms_key_arn           = module.base_kms.kms_key_arn
  app_role_id           = module.base_iam.app_role_id

  instance_class        = var.docdb_instance_class
  instance_count        = var.docdb_instance_count
  deletion_protection   = var.docdb_deletion_protection
  backup_retention_days = var.docdb_backup_retention_days
  log_retention_days    = var.log_retention_days
}

# ---------------------------------------------------------------- 05analytics

module "_05analytics_01athena" {
  source = "./modules/05analytics_01athena"

  prefix                = local.prefix
  region                = var.region
  account_id            = local.account_id
  lake_bucket           = module._03db_03s3.lake_bucket
  athena_results_bucket = module._03db_03s3.athena_results_bucket
  kms_key_arn           = module.base_kms.kms_key_arn
  app_role_id           = module.base_iam.app_role_id

  bytes_scanned_cutoff = var.athena_bytes_scanned_cutoff
}

module "_05analytics_02redshift" {
  source = "./modules/05analytics_02redshift"

  prefix                = local.prefix
  vpc_id                = module.base_network.vpc_id
  subnet_ids            = module.base_network.private_subnet_ids
  app_security_group_id = module.base_network.app_security_group_id
  lake_bucket_arn       = module._03db_03s3.lake_bucket_arn
  kms_key_arn           = module.base_kms.kms_key_arn
  app_role_id           = module.base_iam.app_role_id

  base_rpu = var.redshift_base_rpu
  max_rpu  = var.redshift_max_rpu
}

# ---------------------------------------------------------------- 02messaging

module "_02messaging_01kinesis" {
  source = "./modules/02messaging_01kinesis"

  prefix          = local.prefix
  lake_bucket_arn = module._03db_03s3.lake_bucket_arn
  kms_key_arn     = module.base_kms.kms_key_arn
  app_role_id     = module.base_iam.app_role_id

  stream_mode     = var.kinesis_stream_mode
  shard_count     = var.kinesis_shard_count
  retention_hours = var.kinesis_retention_hours
}

module "_02messaging_02kafka" {
  source = "./modules/02messaging_02kafka"

  prefix                = local.prefix
  region                = var.region
  account_id            = local.account_id
  vpc_id                = module.base_network.vpc_id
  subnet_ids            = module.base_network.private_subnet_ids
  app_security_group_id = module.base_network.app_security_group_id
  kms_key_arn           = module.base_kms.kms_key_arn
  app_role_id           = module.base_iam.app_role_id

  broker_instance_type = var.msk_broker_instance_type
  broker_count         = var.msk_broker_count
  volume_size_gib      = var.msk_volume_size_gib
  log_retention_hours  = var.msk_log_retention_hours
}
