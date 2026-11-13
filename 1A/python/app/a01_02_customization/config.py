"""Slice settings for 01.02 (env prefix A_CUSTOMIZATION_).

- role_arn / s3_prefix = terraform outputs customization_role_arn / customization_s3_prefix.
- provisioned_model_arn is filled by hand after a (deliberate, paid) CreateProvisionedModelThroughput.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CustomizationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_CUSTOMIZATION_", env_file=".env", extra="ignore")

    base_model_id: str = "amazon.nova-micro-v1:0:128k"  # terraform var customization_base_model_id
    role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-customization-role"  # terraform output customization_role_arn
    bucket: str = "a-ai-data-ACCOUNT_ID"  # terraform output data_bucket (00.05)
    prefix: str = "customization"  # train/, validation/, output/ under it
    kms_key_arn: str = ""  # terraform output kms_key_arn; encrypts the custom model artifacts
    dataset_format: str = "conversation"  # conversation (bedrock-conversation-2024) | prompt_completion

    # Hyperparameters: strings, names and ranges per base model (check the model's customization page).
    epoch_count: str = "2"
    batch_size: str = "1"
    learning_rate: str = "0.00001"

    max_record_chars: int = 40_000  # local guard; the real limit is tokens per record per model (quotas page)
    job_poll_timeout_s: int = 6 * 3600  # jobs take hours (order of magnitude)
    provisioned_model_arn: str = ""  # set after create_provisioned_throughput; empty -> converse_custom refuses


@lru_cache
def get_customization_settings() -> CustomizationSettings:
    return CustomizationSettings()
