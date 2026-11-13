"""Slice settings, env prefix A_OBSERVABILITY_. Defaults mirror terraform/05.01.observability.tf."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ObservabilitySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_OBSERVABILITY_", env_file=".env", extra="ignore")

    namespace: str = "A/GenAI"  # the app IAM policy allows PutMetricData only in this namespace
    slice_name: str = "observability"  # value of the Slice dimension
    log_group: str = "/aws/bedrock/a-invocations"  # terraform output invocation_log_group
    sink: str = "cloudwatch"  # cloudwatch (PutMetricData) | emf (log line, extracted by CloudWatch)
    max_metrics_per_call: int = 1000  # PutMetricData limit per call per the CloudWatch API docs: check the quota page
    query_deadline_s: float = 60.0


@lru_cache
def get_observability_settings() -> ObservabilitySettings:
    return ObservabilitySettings()
