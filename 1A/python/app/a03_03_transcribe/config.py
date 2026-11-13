"""Slice settings, env prefix A_TRANSCRIBE_. Defaults mirror terraform/03.03.transcribe.tf."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class TranscribeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_TRANSCRIBE_", env_file=".env", extra="ignore")

    language_code: str = "en-US"
    vocabulary_name: str = "a-vocab"
    filter_name: str = "a-filter"
    filter_method: str = "mask"  # mask (***) | remove | tag (keep text, flag it)
    input_prefix: str = "transcribe/in/"
    output_prefix: str = "transcribe/out/"
    job_prefix: str = "a-"  # IAM policy scopes jobs to transcription-job/a-*
    max_speakers: int = 4  # MaxSpeakerLabels allowed 2..30
    redaction_output: str = "redacted"  # redacted | redacted_and_unredacted
    pii_entity_types: str = "ALL"  # comma list, e.g. "EMAIL,PHONE,CREDIT_DEBIT_NUMBER"; ALL = every supported type
    poll_deadline_s: float = 1800.0


@lru_cache
def get_transcribe_settings() -> TranscribeSettings:
    return TranscribeSettings()
