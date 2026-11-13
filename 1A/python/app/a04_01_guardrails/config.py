"""Slice settings for 04.01 guardrails (env prefix A_GUARDRAILS_).

- Defaults mirror terraform/04.01.guardrails.tf; real ids come from `terraform output`.
- No AWS call here: settings are plain values.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class GuardrailsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_GUARDRAILS_", env_file=".env", extra="ignore")

    guardrail_id: str = "GUARDRAIL_ID"  # terraform output guardrail_id (id or full ARN both work)
    guardrail_version: str = "1"  # terraform output guardrail_version; "DRAFT" only for testing
    guardrail_name: str = "a-guardrail"  # terraform output guardrail_name

    # The configuration-as-code scenario creates its OWN guardrail so it never fights Terraform over a-guardrail.
    sdk_guardrail_name: str = "a-guardrail-sdk"
    kms_key_id: str = "alias/a-data"  # 00.02 CMK; key id, ARN, or alias

    tier: str = "STANDARD"  # CLASSIC | STANDARD (STANDARD needs guardrail_profile_id)
    guardrail_profile_id: str = "us.guardrail.v1:0"  # system cross-Region guardrail profile (us/eu/apac prefix)

    # Automated Reasoning: ARN of an AR policy VERSION; empty = policy not attached (Terraform can't attach it).
    ar_policy_arn: str = ""
    ar_confidence_threshold: float = 1.0  # 0..1; findings below it are reported as translationAmbiguous

    trace: str = "enabled"  # disabled | enabled | enabled_full (full = raw model output in the response)
    stream_mode: str = "sync"  # sync | async (see converse_stream_guarded)
    model_id: str = ""  # empty = app.shared.config text_model_id


@lru_cache
def get_guardrails_settings() -> GuardrailsSettings:
    return GuardrailsSettings()
