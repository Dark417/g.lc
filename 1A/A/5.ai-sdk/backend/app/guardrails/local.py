"""Regex guardrail.

# ILLUSTRATION: catches obvious secrets and PII with regexes. No semantics (jailbreaks, toxicity).
# PRODUCTION: a managed classifier: Bedrock Guardrails (app/guardrails/bedrock.py) or
# Model Armor (app/guardrails/model_armor.py).

Policy:
  INPUT   block secrets (cloud keys, private keys); PII is allowed, users may share their own.
  OUTPUT  mask emails and card numbers; block secrets.
"""

import re

from app.guardrails.base import GuardrailResult, Source

SECRETS = {
    "aws_access_key": re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "anthropic_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
}
PII = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "card_number": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
}


class LocalGuardrail:
    name = "local"

    async def check(self, text: str, source: Source) -> GuardrailResult:
        hits = [name for name, rx in SECRETS.items() if rx.search(text)]
        if hits:
            return GuardrailResult(False, text, [f"secret:{h}" for h in hits])
        if source == "OUTPUT":
            reasons = []
            for name, rx in PII.items():
                if rx.search(text):
                    text = rx.sub(f"[{name.upper()}]", text)
                    reasons.append(f"masked:{name}")
            return GuardrailResult(True, text, reasons)
        return GuardrailResult(True, text)
