# uat — mock values (fake account id, private CIDR). Never applied from this repo.
env            = "uat"
aws_account_id = "222222222222"
region         = "us-east-1"
project_prefix = "x"
use_localstack = false

# base
vpc_cidr                 = "10.30.0.0/16"
az_count                 = 3
kms_deletion_window_days = 14
log_retention_days       = 30

# 03db
aurora_min_acu               = 1
aurora_max_acu               = 8
aurora_instance_count        = 2
aurora_deletion_protection   = true
aurora_backup_retention_days = 7

dynamodb_billing_mode        = "PAY_PER_REQUEST"
dynamodb_read_capacity       = 5
dynamodb_write_capacity      = 5
dynamodb_deletion_protection = true

s3_raw_ia_days                    = 30
s3_raw_glacier_days               = 180
s3_noncurrent_expiration_days     = 30
s3_athena_results_expiration_days = 7

docdb_instance_class        = "db.r6g.large"
docdb_instance_count        = 2
docdb_deletion_protection   = true
docdb_backup_retention_days = 7

# 05analytics
athena_bytes_scanned_cutoff = 10737418240
redshift_base_rpu           = 16
redshift_max_rpu            = 64

# 02messaging
kinesis_stream_mode     = "ON_DEMAND"
kinesis_shard_count     = 1
kinesis_retention_hours = 48

msk_broker_instance_type = "kafka.m7g.large"
msk_broker_count         = 3
msk_volume_size_gib      = 200
msk_log_retention_hours  = 168
