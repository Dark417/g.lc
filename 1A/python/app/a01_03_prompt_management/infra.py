"""Prompt Management showcase (boto3): manage prompts on "bedrock-agent", run them on "bedrock-runtime".

- Order follows docs/01.03.prompt-management.md: create -> edit DRAFT -> version -> get/list -> run.
- Terraform owns a-prompt; create_prompt here shows every console field as code (configuration as code).
- No AWS call at import time.
"""

import uuid
from typing import Any

from app.a01_03_prompt_management.config import PromptsSettings, get_prompts_settings
from app.a01_03_prompt_management.domain import ManagedPrompt, PromptVariant, render_variant
from app.shared import aws

SUMMARY_TEXT = "<task>Summarize {{topic}} for {{audience}}.</task>\n<format>At most 5 bullets.</format>"


def _variant_from_api(v: dict[str, Any]) -> PromptVariant:
    tc = v.get("templateConfiguration", {})
    if v["templateType"] == "TEXT":
        text_cfg = tc.get("text", {})
        variables = [iv["name"] for iv in text_cfg.get("inputVariables", [])]
        return PromptVariant(
            name=v["name"],
            template_type="TEXT",
            model_id=v.get("modelId", ""),
            text=text_cfg.get("text", ""),
            input_variables=variables,
            inference=v.get("inferenceConfiguration", {}).get("text", {}),
        )
    chat = tc.get("chat", {})
    return PromptVariant(
        name=v["name"],
        template_type="CHAT",
        model_id=v.get("modelId", ""),
        system="".join(b.get("text", "") for b in chat.get("system", [])),
        messages=chat.get("messages", []),
        input_variables=[iv["name"] for iv in chat.get("inputVariables", [])],
        inference=v.get("inferenceConfiguration", {}).get("text", {}),
    )


class PromptManagementShowcase:
    def __init__(self, settings: PromptsSettings | None = None) -> None:
        self.settings = settings or get_prompts_settings()

    @property
    def agent(self) -> Any:
        """Control plane for prompts, flows, agents, knowledge bases."""
        return aws.client("bedrock-agent")

    @property
    def runtime(self) -> Any:
        return aws.client("bedrock-runtime")

    # ================================================================ 1.3 create (DRAFT)

    def create_prompt(self, name: str, description: str = "") -> ManagedPrompt:
        """Shows: CreatePrompt with two variants (TEXT + CHAT), input variables, inference config, metadata.
        Same fields as the console's prompt builder. Catch: creates DRAFT only; production needs a version.
        clientToken makes a retried create return the same prompt instead of a duplicate.
        """
        model = self.settings.model()
        inference = {"text": {"maxTokens": 400, "temperature": 0.2, "topP": 0.9, "stopSequences": []}}
        kwargs: dict[str, Any] = {
            "name": name,  # unique per account+Region; ([0-9a-zA-Z][_-]?){1,100}
            "defaultVariant": "default",  # the variant Converse(modelId=prompt ARN) runs
            "variants": [
                {
                    "name": "default",
                    "templateType": "TEXT",  # TEXT | CHAT
                    "templateConfiguration": {
                        "text": {
                            "text": SUMMARY_TEXT,
                            "inputVariables": [{"name": "topic"}, {"name": "audience"}],
                            # "cachePoint": {"type": "default"},  # cache the template prefix (supported models)
                        }
                    },
                    "modelId": model,  # model ID or inference profile
                    "inferenceConfiguration": inference,
                    "metadata": [{"key": "owner", "value": "ai-platform"}],
                },
                {
                    "name": "chat-concise",
                    "templateType": "CHAT",
                    "templateConfiguration": {
                        "chat": {
                            "system": [{"text": "You write for busy {{audience}}. Three bullets, no preamble."}],
                            "messages": [{"role": "user", "content": [{"text": "Summarize {{topic}}."}]}],
                            "inputVariables": [{"name": "topic"}, {"name": "audience"}],
                            # "toolConfiguration": {"tools": [...], "toolChoice": {"auto": {}}},  # CHAT only
                        }
                    },
                    "modelId": model,
                    "inferenceConfiguration": inference,
                    # "additionalModelRequestFields": {"top_k": 50},  # provider-specific keys
                },
            ],
            "clientToken": str(uuid.uuid5(uuid.NAMESPACE_URL, f"prompt/{name}")),  # stable per name ⇒ idempotent
            "tags": {"Component": "01.03"},
        }
        if description:  # optional, but min length 1 when sent
            kwargs["description"] = description
        if self.settings.kms_key_arn:
            kwargs["customerEncryptionKeyArn"] = self.settings.kms_key_arn  # CMK; caller needs KMS permissions
        resp = self.agent.create_prompt(**kwargs)
        return self._to_prompt(resp)

    def update_prompt_draft(self, prompt_id: str, new_text: str) -> ManagedPrompt:
        """Shows: UpdatePrompt edits DRAFT only (versions are immutable). It is a full replace: send every variant,
        or the ones you omit are deleted. Catch: read-modify-write without a version check ⇒ last writer wins.
        """
        current = self.agent.get_prompt(promptIdentifier=prompt_id)  # DRAFT
        variants = current["variants"]
        for v in variants:
            if v["name"] == current["defaultVariant"] and v["templateType"] == "TEXT":
                v["templateConfiguration"]["text"]["text"] = new_text
        optional = {k: current[k] for k in ("description", "customerEncryptionKeyArn") if current.get(k)}
        resp = self.agent.update_prompt(
            promptIdentifier=prompt_id,
            name=current["name"],
            defaultVariant=current["defaultVariant"],
            variants=variants,
            **optional,  # full replace: resend description and the KMS key too, or they are dropped
        )
        return self._to_prompt(resp)

    # ================================================================ 1.4 versions

    def create_prompt_version(self, prompt_id: str, description: str, release_id: str) -> ManagedPrompt:
        """Shows: CreatePromptVersion = immutable snapshot of DRAFT, ARN "<prompt_arn>:<n>".
        Use at release time (after evals pass). Catch: release_id -> clientToken, so a retried release does
        not mint a second version; versions are never edited, only superseded.
        """
        resp = self.agent.create_prompt_version(
            promptIdentifier=prompt_id,
            **({"description": description} if description else {}),
            clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"prompt-version/{prompt_id}/{release_id}")),
            tags={"Component": "01.03", "Release": release_id},
        )
        return self._to_prompt(resp)

    def get_prompt(self, prompt_id: str, version: str | None = None) -> ManagedPrompt:
        """Shows: GetPrompt for DRAFT (no version) or an immutable version. Versions can be cached forever."""
        kwargs: dict[str, str] = {"promptIdentifier": prompt_id}
        if version:
            kwargs["promptVersion"] = version
        return self._to_prompt(self.agent.get_prompt(**kwargs))

    def list_prompts(self) -> list[dict[str, str]]:
        """Shows: ListPrompts with the boto3 paginator (nextToken handled). Returns the DRAFT entry per prompt."""
        out: list[dict[str, str]] = []
        for page in self.agent.get_paginator("list_prompts").paginate(PaginationConfig={"PageSize": 50}):
            for p in page.get("promptSummaries", []):
                out.append({"id": p["id"], "name": p["name"], "arn": p["arn"], "version": p["version"]})
        return out

    def list_versions(self, prompt_id: str) -> list[dict[str, str]]:
        """Shows: ListPrompts(promptIdentifier=...) lists the versions of one prompt (manual nextToken loop)."""
        out: list[dict[str, str]] = []
        token: str | None = None
        while True:
            kwargs: dict[str, Any] = {"promptIdentifier": prompt_id, "maxResults": 50}
            if token:
                kwargs["nextToken"] = token
            resp = self.agent.list_prompts(**kwargs)
            out += [{"version": p["version"], "arn": p["arn"]} for p in resp.get("promptSummaries", [])]
            token = resp.get("nextToken")
            if not token:
                return out

    # ================================================================ 1.5 run

    def converse_managed_prompt(self, prompt_version_arn: str, variables: dict[str, str]) -> dict[str, Any]:
        """Shows: Converse with modelId = prompt version ARN + promptVariables; Bedrock renders the default variant
        and uses its model + inference config. Catch: system / inferenceConfig / toolConfig /
        additionalModelRequestFields are not allowed in this call; DRAFT ARN (no ":n") is for testing only.
        """
        if ":" not in prompt_version_arn.rsplit("/", 1)[-1]:
            raise ValueError("pin a version ARN (<prompt_arn>:<n>); DRAFT is not for production")
        resp = self.runtime.converse(
            modelId=prompt_version_arn,
            promptVariables={k: {"text": v} for k, v in variables.items()},  # PromptVariableValues = {"text": ...}
        )
        return {
            "text": "".join(b.get("text", "") for b in resp["output"]["message"]["content"]),
            "stop_reason": resp["stopReason"],
            "usage": resp.get("usage", {}),
        }

    def converse_rendered_variant(self, prompt_id: str, version: str, variant: str, variables: dict[str, str]) -> dict[str, Any]:
        """Shows: GetPrompt -> render any variant locally -> Converse with that variant's model and settings.
        Use for A/B between variants, or to add your own guardrail/system text. Catch: you now own rendering
        rules (strict variables) and should cache GetPrompt per version.
        """
        chosen = self.get_prompt(prompt_id, version).variant(variant)
        system, messages = render_variant(chosen, variables)
        inf = chosen.inference
        kwargs: dict[str, Any] = {
            "modelId": chosen.model_id,
            "messages": messages,
            "inferenceConfig": {k: inf[k] for k in ("maxTokens", "temperature", "topP", "stopSequences") if inf.get(k) not in (None, [])},
        }
        if system:
            kwargs["system"] = [{"text": system}]
        resp = self.runtime.converse(**kwargs)
        return {
            "variant": chosen.name,
            "text": "".join(b.get("text", "") for b in resp["output"]["message"]["content"]),
            "stop_reason": resp["stopReason"],
        }

    @staticmethod
    def _to_prompt(resp: dict[str, Any]) -> ManagedPrompt:
        return ManagedPrompt(
            prompt_id=resp["id"],
            arn=resp["arn"],
            version=resp.get("version", "DRAFT"),
            default_variant=resp.get("defaultVariant", ""),
            variants=[_variant_from_api(v) for v in resp.get("variants", [])],
        )
