# local — mock values (fake account id, private CIDR). Never applied from this repo.
env                 = "local"
aws_account_id      = "000000000000"
region              = "us-east-1"
project_prefix      = "x"
use_localstack      = true
localstack_endpoint = "http://localhost:4566"

# base
vpc_cidr                 = "10.10.0.0/16"
az_count                 = 2
kms_deletion_window_days = 7
log_retention_days       = 3

# 03db
aurora_min_acu               = 0.5
aurora_max_acu               = 2
aurora_instance_count        = 1
aurora_deletion_protection   = false
aurora_backup_retention_days = 1

dynamodb_billing_mode        = "PAY_PER_REQUEST"
dynamodb_read_capacity       = 5
dynamodb_write_capacity      = 5
dynamodb_deletion_protection = false

s3_raw_ia_days                    = 30
s3_raw_glacier_days               = 60
s3_noncurrent_expiration_days     = 7
s3_athena_results_expiration_days = 1

docdb_instance_class        = "db.t4g.medium"
docdb_instance_count        = 1
docdb_deletion_protection   = false
docdb_backup_retention_days = 1

# 05analytics
athena_bytes_scanned_cutoff = 1073741824
redshift_base_rpu           = 8
redshift_max_rpu            = 8

# 02messaging
kinesis_stream_mode     = "PROVISIONED"
kinesis_shard_count     = 1
kinesis_retention_hours = 24

msk_broker_instance_type = "kafka.t3.small"
msk_broker_count         = 2
msk_volume_size_gib      = 10
msk_log_retention_hours  = 24
