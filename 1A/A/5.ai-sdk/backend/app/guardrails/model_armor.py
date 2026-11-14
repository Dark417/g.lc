"""Google Cloud Model Armor: prompt and response screening against a template.

The template (created in the console or with gcloud, see infra/gcp/README.md) decides which
filters run: prompt injection and jailbreak, responsible AI, sensitive data (DLP), malicious URLs.
"""

import asyncio

from app.guardrails.base import GuardrailResult, Source


class ModelArmorGuardrail:
    name = "model_armor"

    def __init__(self, template: str, client=None):
        # template = projects/{p}/locations/{loc}/templates/{id}
        self.template = template
        self._client = client

    @property
    def client(self):
        if self._client is None:
            from google.cloud import modelarmor_v1

            location = self.template.split("/locations/")[1].split("/")[0]
            self._client = modelarmor_v1.ModelArmorClient(
                client_options={"api_endpoint": f"modelarmor.{location}.rep.googleapis.com"}
            )
        return self._client

    def _sanitize(self, text: str, source: Source):
        from google.cloud import modelarmor_v1 as ma

        item = ma.DataItem(text=text)
        if source == "INPUT":
            req = ma.SanitizeUserPromptRequest(name=self.template, user_prompt_data=item)
            return self.client.sanitize_user_prompt(request=req)
        req = ma.SanitizeModelResponseRequest(name=self.template, model_response_data=item)
        return self.client.sanitize_model_response(request=req)

    async def check(self, text: str, source: Source) -> GuardrailResult:
        from google.cloud import modelarmor_v1 as ma

        resp = await asyncio.to_thread(self._sanitize, text, source)
        result = resp.sanitization_result
        if result.filter_match_state == ma.FilterMatchState.MATCH_FOUND:
            reasons = [k for k, v in result.filter_results.items() if "MATCH_FOUND" in str(v)]
            return GuardrailResult(False, text, reasons or ["model_armor:match"])
        return GuardrailResult(True, text)
