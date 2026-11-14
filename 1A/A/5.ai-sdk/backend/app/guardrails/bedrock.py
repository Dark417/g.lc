"""Amazon Bedrock Guardrails via the standalone ApplyGuardrail API.

ApplyGuardrail works on any text, so it guards every framework the same way, including models
not hosted on Bedrock. The native alternative is attaching the guardrail to the model call
itself, shown in the Strands adapter: BedrockModel(guardrail_id=..., guardrail_version=...).
"""

import asyncio
import json

import boto3

from app.guardrails.base import GuardrailResult, Source


class BedrockGuardrail:
    name = "bedrock_guardrails"

    def __init__(self, guardrail_id: str, version: str, region: str, client=None):
        self.guardrail_id = guardrail_id
        self.version = version
        self._client = client or boto3.client("bedrock-runtime", region_name=region)

    async def check(self, text: str, source: Source) -> GuardrailResult:
        resp = await asyncio.to_thread(
            self._client.apply_guardrail,
            guardrailIdentifier=self.guardrail_id,
            guardrailVersion=self.version,
            source=source,
            content=[{"text": {"text": text}}],
        )
        if resp.get("action") != "GUARDRAIL_INTERVENED":
            return GuardrailResult(True, text)
        outputs = resp.get("outputs") or []
        replaced = outputs[0]["text"] if outputs else text
        assessments = resp.get("assessments", [])
        reasons = sorted({k for a in assessments for k in a if k.endswith("Policy")}) or [
            "intervened"
        ]
        # PII "ANONYMIZED" interventions only mask; any "BLOCKED" action stops the text.
        blocked = '"BLOCKED"' in json.dumps(assessments)
        return GuardrailResult(not blocked, replaced, reasons)
