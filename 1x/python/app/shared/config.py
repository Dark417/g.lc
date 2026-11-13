"""Settings from environment variables (pydantic-settings).

- Every slice is off unless listed in X_ENABLED (comma list), e.g. X_ENABLED=aurora,dynamodb.
- Resource names match Terraform outputs in 1x/terraform (prefix "x").
- No secrets here: Aurora uses IAM auth tokens, AWS uses the default credential chain.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="X_", env_file=".env", extra="ignore")

    enabled: str = ""
    aws_region: str = "us-east-1"

    # 03.01 Aurora PostgreSQL
    aurora_writer_endpoint: str = "x-aurora.cluster-EXAMPLE.us-east-1.rds.amazonaws.com"
    aurora_reader_endpoint: str = "x-aurora.cluster-ro-EXAMPLE.us-east-1.rds.amazonaws.com"
    aurora_port: int = 5432
    aurora_database: str = "xdb"
    aurora_username: str = "x_app"
    aurora_iam_auth: bool = True
    aurora_pool_max_size: int = 10
    aurora_pool_max_lifetime_s: int = 840  # 14 min: < 15 min IAM token life

    # 03.02 DynamoDB
    dynamodb_orders_table: str = "x-orders"
    dynamodb_idempotency_table: str = "x-idempotency"
    dynamodb_gsi1_name: str = "GSI1"

    # 03.03 S3
    s3_lake_bucket: str = "x-lake-ACCOUNT_ID"
    s3_athena_results_bucket: str = "x-athena-results-ACCOUNT_ID"
    s3_kms_key_alias: str = "alias/x-data"

    # 04.01 Athena
    athena_workgroup: str = "x-wg"
    athena_database: str = "x_lake"

    # 04.02 Redshift
    redshift_workgroup: str = "x-dw"
    redshift_database: str = "dev"

    # 05.01 Kinesis + Firehose
    kinesis_stream: str = "x-clicks"
    firehose_stream: str = "x-events"

    # 05.02 Kafka (MSK)
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_iam_auth: bool = False

    def enabled_slices(self) -> set[str]:
        return {s.strip() for s in self.enabled.split(",") if s.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
