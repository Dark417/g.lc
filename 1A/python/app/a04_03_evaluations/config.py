"""Slice settings for 04.03 evaluations (env prefix A_EVALS_).

- Defaults mirror terraform/04.03.evaluations.tf (role a-bedrock-eval, evals/datasets|results prefixes).
- Guardrail + KB ids are repeated here (not imported from other slices); they point at the same terraform outputs.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class EvalsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_EVALS_", env_file=".env", extra="ignore")

    role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-bedrock-eval"  # terraform output bedrock_eval_role_arn
    datasets_prefix: str = "evals/datasets/"
    results_prefix: str = "evals/results/"
    kms_key_id: str = "alias/a-data"  # customerEncryptionKeyId for results

    # Generator = model under test; judge = evaluator. Different families reduce self-preference bias.
    # The judge must be on the supported evaluator list (check the docs; it changes).
    generator_model_id: str = ""  # empty = app.shared.config fast_model_id
    judge_model_id: str = "us.amazon.nova-pro-v1:0"

    knowledge_base_id: str = "KB_ID"  # terraform output of 02.04 (knowledge base)
    rag_number_of_results: int = 5  # top-k for the RAG eval (1..100)

    guardrail_id: str = "GUARDRAIL_ID"  # terraform output guardrail_id (04.01)
    guardrail_version: str = "DRAFT"  # evaluate the candidate (DRAFT) before creating a version


@lru_cache
def get_evals_settings() -> EvalsSettings:
    return EvalsSettings()
