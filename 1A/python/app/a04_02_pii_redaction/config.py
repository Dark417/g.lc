"""Slice settings for 04.02 PII redaction (env prefix A_PII_).

- Defaults mirror terraform/04.02.pii-redaction.tf (role a-comprehend-pii, comprehend/input|output prefixes).
- The guardrail used as the output net is configured here too (A_PII_GUARDRAIL_ID) so this slice does not import
  the 04.01 package; both point at the same terraform output guardrail_id.
- hmac_key: demo only. In prod load it from Secrets Manager / KMS-encrypted config, never from a default.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class PiiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_PII_", env_file=".env", extra="ignore")

    language_code: str = "en"  # PII detection: en | es (check the docs for current languages)
    min_score: float = 0.8  # default confidence threshold; per-type overrides live in RedactionPolicy

    data_access_role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-comprehend-pii"  # output comprehend_pii_role_arn
    input_prefix: str = "comprehend/input/"
    output_prefix: str = "comprehend/output/"
    kms_key_id: str = "alias/a-data"  # encrypts job output (OutputDataConfig.KmsKeyId)

    guardrail_id: str = "GUARDRAIL_ID"  # terraform output guardrail_id (04.01)
    guardrail_version: str = "1"
    model_id: str = ""  # empty = app.shared.config fast_model_id

    hmac_key: str = ""  # empty = random per process (tokens not stable across restarts)
    stream_window: int = 64  # chars held back by the streaming redactor


@lru_cache
def get_pii_settings() -> PiiSettings:
    return PiiSettings()
