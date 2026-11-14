# dev — mock values (fake account id, private CIDR). Never applied from this repo.
env            = "dev"
aws_account_id = "111111111111"
region         = "us-east-1"
project_prefix = "x"
use_localstack = false

# base
vpc_cidr                 = "10.20.0.0/16"
az_count                 = 2
kms_deletion_window_days = 7
log_retention_days       = 7

# 03db
aurora_min_acu               = 0.5
aurora_max_acu               = 4
aurora_instance_count        = 1
aurora_deletion_protection   = false
aurora_backup_retention_days = 3

dynamodb_billing_mode        = "PAY_PER_REQUEST"
dynamodb_read_capacity       = 5
dynamodb_write_capacity      = 5
dynamodb_deletion_protection = false

s3_raw_ia_days                    = 30
s3_raw_glacier_days               = 90
s3_noncurrent_expiration_days     = 14
s3_athena_results_expiration_days = 3

docdb_instance_class        = "db.t4g.medium"
docdb_instance_count        = 1
docdb_deletion_protection   = false
docdb_backup_retention_days = 3

# 05analytics
athena_bytes_scanned_cutoff = 1073741824
redshift_base_rpu           = 8
redshift_max_rpu            = 16

# 02messaging
kinesis_stream_mode     = "PROVISIONED"
kinesis_shard_count     = 2
kinesis_retention_hours = 24

msk_broker_instance_type = "kafka.t3.small"
msk_broker_count         = 2
msk_volume_size_gib      = 50
msk_log_retention_hours  = 72
