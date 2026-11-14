# prod — mock values (fake account id, private CIDR). Never applied from this repo.
env            = "prod"
aws_account_id = "333333333333"
region         = "us-east-1"
project_prefix = "x"
use_localstack = false

# base
vpc_cidr                 = "10.40.0.0/16"
az_count                 = 3
kms_deletion_window_days = 30
log_retention_days       = 365

# 03db
aurora_min_acu               = 2
aurora_max_acu               = 32
aurora_instance_count        = 3
aurora_deletion_protection   = true
aurora_backup_retention_days = 35

dynamodb_billing_mode        = "PROVISIONED"
dynamodb_read_capacity       = 200
dynamodb_write_capacity      = 100
dynamodb_deletion_protection = true

s3_raw_ia_days                    = 60
s3_raw_glacier_days               = 365
s3_noncurrent_expiration_days     = 90
s3_athena_results_expiration_days = 30

docdb_instance_class        = "db.r6g.xlarge"
docdb_instance_count        = 3
docdb_deletion_protection   = true
docdb_backup_retention_days = 35

# 05analytics
athena_bytes_scanned_cutoff = 107374182400
redshift_base_rpu           = 32
redshift_max_rpu            = 256

# 02messaging
kinesis_stream_mode     = "ON_DEMAND"
kinesis_shard_count     = 1
kinesis_retention_hours = 168

msk_broker_instance_type = "kafka.m7g.xlarge"
msk_broker_count         = 6
msk_volume_size_gib      = 1000
msk_log_retention_hours  = 168
